<div align="center">

![Laboratorio AWS](https://img.shields.io/badge/-LABORATORIO%20AWS-ff69b4?style=for-the-badge&logoColor=white)

# Automatización de solicitudes con API Gateway, EventBridge y Step Functions

![API Gateway](https://img.shields.io/badge/-API%20Gateway-ff8fc7?style=flat-square&logoColor=white)
![Lambda](https://img.shields.io/badge/-Lambda-d63384?style=flat-square&logoColor=white)
![EventBridge](https://img.shields.io/badge/-EventBridge-e75480?style=flat-square&logoColor=white)
![Step Functions](https://img.shields.io/badge/-Step%20Functions-ff69b4?style=flat-square&logoColor=white)
![Python 3.11](https://img.shields.io/badge/-Python%203.11-ff8fc7?style=flat-square&logoColor=white)

*Procesamiento serverless de pedidos en AWS*

</div>

---

## ![Descripción](https://img.shields.io/badge/-Descripci%C3%B3n-ff69b4?style=for-the-badge&logoColor=white)

En este laboratorio se construyó un flujo **serverless** que recibe pedidos por una API, los publica como evento y los procesa automáticamente paso a paso: validación, revisión de inventario, pago, confirmación y auditoría. No hay servidores que administrar: cada pieza se ejecuta solo cuando llega un pedido.

---

## ![Arquitectura](https://img.shields.io/badge/-Arquitectura-ff69b4?style=for-the-badge&logoColor=white)

```mermaid
flowchart LR
    A(["Cliente<br/>Postman"]) -->|"POST /order"| B["API Gateway<br/>HTTP API"]
    B --> C["Lambda<br/>receive-order"]
    C -->|"PutEvents<br/>NuevoPedido"| D["EventBridge<br/>regla"]
    D --> E["Step Functions<br/>máquina de estados"]
    E --> F["Lambdas<br/>validate · inventory<br/>payment · confirm · audit"]
    classDef pink fill:#ffe0f0,stroke:#ff69b4,stroke-width:2px,color:#7a1250
    class A,B,C,D,E,F pink
```

---

## ![Qué se hizo](https://img.shields.io/badge/-Qu%C3%A9%20se%20hizo-ff69b4?style=for-the-badge&logoColor=white)

| Servicio | Qué se configuró |
|---|---|
| 🌸 **AWS Lambda** | Seis funciones en Python 3.11: `receive-order`, `validate-order`, `check-inventory`, `process-payment`, `confirm-order` y `register-audit` |
| 🌸 **IAM** | Permiso `events:PutEvents` para que `receive-order` pueda publicar eventos |
| 🌸 **Step Functions** | Máquina de estados *Standard* que encadena las Lambdas con decisiones y estados de falla |
| 🌸 **EventBridge** | Regla en el bus `default` que escucha `source: demo.pedidos` y `detail-type: NuevoPedido` y lanza la máquina de estados |
| 🌸 **API Gateway** | HTTP API con la ruta `POST /order` conectada a la Lambda `receive-order` |

---

## ![Lógica del pedido](https://img.shields.io/badge/-L%C3%B3gica%20del%20pedido-ff69b4?style=for-the-badge&logoColor=white)

```mermaid
flowchart TD
    S(["Inicio"]) --> V["ValidateOrder"]
    V --> VC{"¿Pedido válido?"}
    VC -->|"No"| F1(["InvalidOrder"])
    VC -->|"Sí"| I["CheckInventory"]
    I --> IC{"¿Hay stock?"}
    IC -->|"No"| F2(["OutOfStock"])
    IC -->|"Sí"| P["ProcessPayment"]
    P --> PC{"¿Pago aprobado?"}
    PC -->|"No"| F3(["PaymentRejected"])
    PC -->|"Sí"| W["Espera de 5 s"]
    W --> C["ConfirmOrder"]
    C --> A["RegisterAudit"]
    A --> OK(["Éxito"])
    classDef ok fill:#ffe0f0,stroke:#ff69b4,stroke-width:2px,color:#7a1250
    classDef fail fill:#fff,stroke:#d63384,stroke-width:2px,color:#d63384
    class S,V,VC,I,IC,P,PC,W,C,A,OK ok
    class F1,F2,F3 fail
```

- ✅ **Validación:** cliente y producto no vacíos, cantidad y total mayores que 0.
- 📦 **Inventario:** hay stock si la cantidad es menor o igual a 5.
- 💳 **Pago:** se aprueba si el total es menor o igual a 1000.

---

## ![Contenido del PDF](https://img.shields.io/badge/-Contenido%20del%20PDF-ff69b4?style=for-the-badge&logoColor=white)

El archivo [MariaCamilaMejiaArango-Laboratorio-StepFunctions.pdf](./MariaCamilaMejiaArango-Laboratorio-StepFunctions.pdf) reúne las evidencias del laboratorio, en este orden:

1. 🌷 Funciones Lambda creadas
2. 🌷 Definición de la máquina de estados (JSON)
3. 🌷 Diagrama de la máquina de estados en Step Functions
4. 🌷 API Gateway: API HTTP `api-camilamejia`
5. 🌷 Prueba de la URL de la API en el navegador
6. 🌷 Prueba de la API con Postman

---

## ![Cómo probarlo](https://img.shields.io/badge/-C%C3%B3mo%20probarlo-ff69b4?style=for-the-badge&logoColor=white)

Envía un `POST` a la URL de invocación de la API más la ruta `/order`, con este cuerpo JSON:

```json
{
  "cliente": "Johan",
  "producto": "Laptop",
  "cantidad": 1,
  "total": 900
}
```

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/order \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Johan","producto":"Laptop","cantidad":1,"total":900}'
```

La API responde con un `orderId`, y el resultado del procesamiento se ve en **Step Functions → Ejecuciones**. Para recorrer los otros caminos:

| Cambio en el cuerpo | Resultado esperado |
|---|---|
| `"cantidad": 6` | Termina en `OutOfStock` |
| `"total": 1500` | Termina en `PaymentRejected` |
| `"cliente": ""` | Termina en `InvalidOrder` |

---

## ![Limpieza](https://img.shields.io/badge/-Limpieza-ff69b4?style=for-the-badge&logoColor=white)

Al terminar la práctica se eliminan los recursos creados (API, regla de EventBridge, máquina de estados y Lambdas con sus roles y registros) para evitar costos innecesarios.

---

<div align="center">

Hecho con 💗 por **Maria Camila Mejia Arango**

*Bootcamp de computación en la nube*

</div>
