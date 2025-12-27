# Arquitectura del Sistema de Detección

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOG COMPUTING (Local)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Sensores │  │  Cámaras │  │    ML    │  │  API     │         │
│  │  Temp/   │→ │  Video   │→ │ Detection│→ │  Local   │         │
│  │ Humedad  │  │  Stream  │  │  Model   │  │          │         │
│  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘         │
└─────────────────────────────────────────────────┼───────────────┘
                                                     │ HTTPS
                                                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD COMPUTING (AWS)                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              API Gateway HTTP API                         │  │
│  │  Endpoint: https://xxx.execute-api.us-east-1.amazonaws.com│  │
│  └───────┬───────────────────────────────────────────────┬───┘  │
│          │                                               │      │
│          ├──── POST /sensor-data                         │      │
│          ├──── POST /sensor-status                       │      │
│          ├──── GET  /sensor-data                         │      │
│          ├──── GET  /ml-detection                        │      │
│          ├──── GET  /alerts                              │      │
│          ├──── GET  /sensor-status                       │      │
│          └──── GET  /alerts/send                         │      │
│                │                                         │      │
│                ↓                                         │      │
│  ┌─────────────────────────────────────────────────┐     │      │
│  │         AWS LAMBDA FUNCTIONS (Python 3.11)      │     │      │
│  ├─────────────────────────────────────────────────┤     │      │
│  │ 1. insert_sensor_data      [POST]               │◄────┘      │
│  │    - Valida datos                               │            │
│  │    - Guarda en DynamoDB                         │            │
│  │    - Verifica umbrales                          │────┐       │
│  │    - Dispara alertas si es necesario            │    │       │
│  ├─────────────────────────────────────────────────┤    │       │
│  │ 2. insert_sensor_status    [POST]               │    │       │
│  │    - Registra estado sensores/cámaras           │    │       │
│  ├─────────────────────────────────────────────────┤    │       │
│  │ 3. send_alerts            [GET/Invoke]          │◄───┤       │
│  │    - Genera mensajes de email                   │    │       │
│  │    - Publica en SNS                             │    │       │
│  │    - Registra en tabla alerts                   │────┼─┐     │
│  ├─────────────────────────────────────────────────┤    │ │     │
│  │ 4. get_sensor_data        [GET]                 │    │ │     │
│  │    - Consulta datos con filtros                 │    │ │     │
│  ├─────────────────────────────────────────────────┤    │ │     │
│  │ 5. get_ml_detection       [GET]                 │    │ │     │
│  │    - Retorna probabilidades ML                  │    │ │     │
│  ├─────────────────────────────────────────────────┤    │ │     │
│  │ 6. get_alerts             [GET]                 │    │ │     │
│  │    - Retorna historial alertas                  │    │ │     │
│  ├─────────────────────────────────────────────────┤    │ │     │
│  │ 7. check_sensor_status    [Scheduled]           │    │ │     │
│  │    - Ejecuta cada 2 horas (EventBridge)         │────┘ │     │
│  │    - Verifica estado sensores                   │      │     │
│  │    - Dispara alertas si hay fallos              │      │     │
│  ├─────────────────────────────────────────────────┤      │     │
│  │ 8. get_sensor_status      [GET]                 │      │     │
│  │    - Estado actual de sensores                  │      │     │
│  └────────┬────────────────────────────────────┬───┘      │     │
│           │                                    │          │     │
│           ↓                                    ↓          ↓     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐     │
│  │   DynamoDB      │  │   DynamoDB      │  │  DynamoDB    │     │
│  │  sensor_data    │  │ sensor_status   │  │   alerts     │     │
│  ├─────────────────┤  ├─────────────────┤  ├──────────────┤     │
│  │ PK: id          │  │ PK: id          │  │ PK: alert_id │     │
│  │ SK: timestamp   │  │ SK: timestamp   │  │ SK: timestamp│     │
│  │ - temperature   │  │ - alert         │  │ - alert_type │     │
│  │ - humidity      │  │ - sensors ok    │  │ - payload    │     │
│  │ - prob_vapor    │  │ - cameras ok    │  │ - sns_id     │     │
│  │ - prob_smug     │  │ - status list   │  │ - status     │     │
│  │ - prob_smoke    │  │                 │  │              │     │
│  │ - prob_fog      │  │ GSI: has_alert  │  │ GSI: type    │     │
│  │ - alert_level   │  │                 │  │              │     │
│  │                 │  │                 │  │              │     │
│  │ GSI: alert_level│  │                 │  │              │     │
│  └─────────────────┘  └─────────────────┘  └──────────────┘     │
│                                                     │           │
│                                                     ↓           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  Amazon SNS Topic                         │  │
│  │              fog-smoke-detection-alerts                   │  │
│  └─────────┬─────────────────────────────────────────────┬───┘  │
│            │                                             │      │
│            ↓                                             ↓      │
│  ┌───────────────────┐                         ┌──────────────┐ │
│  │ Email Subscription│                         │Email Subscr. │ │
│  │santiagovl0308@... │                         │jeiboxgmr@... │ │
│  └───────────────────┘                         └──────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Amazon EventBridge                           │  │
│  │  Rule: Every 2 hours → Trigger check_sensor_status        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 IAM Roles & Policies                      │  │
│  │  - Lambda execution role                                  │  │
│  │  - DynamoDB read/write permissions                        │  │
│  │  - SNS publish permissions                                │  │
│  │  - Lambda invoke permissions                              │  │
│  │  - CloudWatch logs permissions                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              CloudWatch Logs                              │  │
│  │  /aws/lambda/fog-smoke-detection-*                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos Principal

### 1. Inserción de Datos (POST /sensor-data)

```
API Fog Computing
       │
       ↓
API Gateway (valida request)
       │
       ↓
Lambda: insert_sensor_data
       ├──→ Valida campos requeridos
       ├──→ Convierte a Decimal
       ├──→ Verifica umbrales:
       │    • Temperatura > 45°C
       │    • Humedad < 10%
       │    • Probabilidad humo > 70%
       │    • Probabilidad niebla > 60% (CRÍTICO - Peligro Vial)
       │
       ├──→ Guarda en DynamoDB (sensor_data)
       │
       └──→ Si umbral superado:
            └──→ Invoca send_alerts (asíncrono)
                 ├──→ Genera mensaje email
                 ├──→ Publica en SNS
                 └──→ Registra en DynamoDB (alerts)
                      └──→ SNS envía emails
```

### 2. Verificación Periódica (Cada 2 horas)

```
EventBridge Timer (cada 2 horas)
       │
       ↓
Lambda: check_sensor_status
       ├──→ Query sensor_status (últimos registros)
       ├──→ Verifica estado:
       │    • Sensor de humedad
       │    • Sensor de temperatura
       │    • Estado de cámaras
       │
       └──→ Si hay fallos:
            └──→ Invoca send_alerts
                 └──→ Notifica por email
```

### 3. Consulta de Datos (GET /sensor-data)

```
Cliente HTTP
       │
       ↓
API Gateway
       │
       ↓
Lambda: get_sensor_data
       ├──→ Parse query params (limit, alert_level)
       ├──→ Query/Scan DynamoDB
       ├──→ Ordena por timestamp
       └──→ Retorna JSON
```

## Características Serverless

✅ **Sin servidores que gestionar**
- Todas las funciones Lambda escalan automáticamente
- DynamoDB con facturación pay-per-request
- API Gateway HTTP (sin necesidad de configurar infraestructura)

✅ **Alta disponibilidad**
- Multi-AZ por defecto en todos los servicios
- Point-in-time recovery en DynamoDB
- Reintentos automáticos en Lambda

✅ **Bajo costo**
- Pago solo por uso real
- Free tier generoso
- Sin costos de infraestructura ociosa

✅ **Seguridad**
- IAM roles con permisos mínimos
- Encriptación en tránsito y reposo
- VPC opcional para mayor aislamiento

## Umbrales Configurados

| Parámetro | Umbral | Acción |
|-----------|--------|--------|
| Temperatura | > 45°C | Genera alerta DANGER |
| Humedad | < 10% (0.10) | Genera alerta DANGER |
| Prob. Humo | > 70% (0.70) | Genera alerta DANGER |
| **Prob. Niebla** | **> 60% (0.60)** | **CRÍTICO - PELIGRO VIAL** |
| Estado sensor | `status: false` | Email cada 2h si persiste |
| Estado cámara | `status: false` | Email cada 2h si persiste |

## Escalabilidad

- **Lambda**: Hasta 1000 ejecuciones concurrentes (ajustable)
- **DynamoDB**: Escala automáticamente según demanda
- **API Gateway**: Maneja millones de requests
- **SNS**: Sin límite de mensajes

## Monitoreo

- **CloudWatch Logs**: Todos los logs de Lambda
- **CloudWatch Metrics**: Métricas automáticas de todos los servicios
- **X-Ray**: Trazabilidad opcional (configurable)
- **DynamoDB Insights**: Monitoreo de tablas
