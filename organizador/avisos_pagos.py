#!/usr/bin/env python3
"""
Avisos de pagos del Organizador financiero.

Lee la copia que guardas con el botón "Guardar copia" de la página
(organizador-financiero.json) y te manda una notificación del sistema
2 días antes, el día del pago y cuando ya venció.

No necesita instalar nada (solo Python 3). Funciona en Windows, macOS y Linux.

Uso:
  python avisos_pagos.py              -> queda corriendo y revisa cada 30 minutos
  python avisos_pagos.py --probar     -> manda una notificación de prueba
  python avisos_pagos.py --una-vez    -> revisa una sola vez y termina
  python avisos_pagos.py ruta.json    -> usa un archivo específico

En Windows, para que arranque solo y sin ventana: cambia el nombre a
avisos_pagos.pyw y pon un acceso directo en la carpeta de inicio
(Win + R, escribe shell:startup).
"""
import glob
import json
import os
import platform
import subprocess
import sys
import time
from datetime import date, datetime

DIAS_ANTES = 2
CADA_MINUTOS = 30
PATRON = "organizador-financiero*.json"
CARPETAS = [
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Descargas"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Documentos"),
    os.path.dirname(os.path.abspath(__file__)),
]
ESTADO = os.path.join(os.path.expanduser("~"), ".avisos_pagos_estado.json")


def notificar(titulo, mensaje):
    sistema = platform.system()
    try:
        if sistema == "Windows":
            t, m = titulo.replace("'", "''"), mensaje.replace("'", "''")
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "Add-Type -AssemblyName System.Drawing;"
                "$n = New-Object System.Windows.Forms.NotifyIcon;"
                "$n.Icon = [System.Drawing.SystemIcons]::Information;"
                "$n.Visible = $true;"
                f"$n.ShowBalloonTip(10000, '{t}', '{m}', 'Info');"
                "Start-Sleep -Seconds 11; $n.Dispose()"
            )
            subprocess.Popen(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                creationflags=0x08000000,  # sin ventana
            )
        elif sistema == "Darwin":
            t, m = titulo.replace('"', "'"), mensaje.replace('"', "'")
            subprocess.run(
                ["osascript", "-e", f'display notification "{m}" with title "{t}"']
            )
        else:
            subprocess.run(["notify-send", titulo, mensaje])
    except Exception as e:
        print(f"No pude mostrar la notificación: {e}")
    print(f"[{datetime.now():%H:%M}] {titulo} - {mensaje}")


def buscar_copia(ruta_dada=None):
    if ruta_dada:
        return ruta_dada if os.path.exists(ruta_dada) else None
    candidatos = []
    for carpeta in CARPETAS:
        candidatos += glob.glob(os.path.join(carpeta, PATRON))
    return max(candidatos, key=os.path.getmtime) if candidatos else None


def cargar_estado():
    try:
        with open(ESTADO, encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def guardar_estado(vistos):
    try:
        with open(ESTADO, "w", encoding="utf-8") as f:
            json.dump(sorted(vistos)[-300:], f)
    except Exception:
        pass


def cuando(dias):
    if dias < 0:
        return f"venció hace {-dias} {'día' if dias == -1 else 'días'}"
    if dias == 0:
        return "vence hoy"
    if dias == 1:
        return "vence mañana"
    return f"vence en {dias} días"


def plata(n):
    return "$ " + f"{int(n or 0):,}".replace(",", ".")


def revisar(ruta_dada=None):
    vistos = cargar_estado()
    hoy = date.today()
    ruta = buscar_copia(ruta_dada)
    if not ruta:
        clave = f"sin-copia|{hoy}"
        if clave not in vistos:
            vistos.add(clave)
            notificar(
                "Organizador financiero",
                "No encuentro la copia. Usa 'Guardar copia' en la página.",
            )
            guardar_estado(vistos)
        return
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
    except Exception as e:
        print(f"No pude leer {ruta}: {e}")
        return

    for r in datos.get("rows", []):
        if r.get("paid") or not r.get("date"):
            continue
        dias = (datetime.strptime(r["date"], "%Y-%m-%d").date() - hoy).days
        if dias > DIAS_ANTES:
            continue
        clave = f"{r.get('id')}|{r['date']}|{max(dias, -1)}"
        if clave in vistos:
            continue
        vistos.add(clave)
        nombre = r.get("name") or "Pago sin nombre"
        notificar(f"{nombre} {cuando(dias)}", plata(r.get("amount")))
    guardar_estado(vistos)


def main():
    args = sys.argv[1:]
    if "--probar" in args:
        notificar("Organizador financiero", "Así se verán tus avisos de pago.")
        return
    ruta = next((a for a in args if not a.startswith("--")), None)
    una_vez = "--una-vez" in args
    while True:
        revisar(ruta)
        if una_vez:
            break
        time.sleep(CADA_MINUTOS * 60)


if __name__ == "__main__":
    main()
