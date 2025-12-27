# Sistema de Detección de Niebla y Humo - Fog + Cloud Computing

Este proyecto implementa un **sistema completo e inteligente** de detección temprana de niebla y humo en entornos urbanos, utilizando una arquitectura híbrida que combina **Fog Computing** (procesamiento local) y **Cloud Computing** (almacenamiento y alertas serverless en AWS).

## 🎯 Componentes del Sistema

### 1. FOG COMPUTING (Edge/Local Processing)
- **Flask API** con detección temprana inteligente
- **Sensores** de temperatura y humedad
- **Cámara IP** para captura de video (192.168.2.134)
- **Visión por Computadora** sin ML (OpenCV)
- **Análisis en tiempo real** con umbrales configurables

👉 [Ver documentación completa de Fog Computing](FOG_COMPUTING_README.md)

### 2. CLOUD COMPUTING (AWS Serverless)
- **8 Microservicios Lambda** (Python 3.11)
- **3 Tablas DynamoDB** serverless
- **API Gateway HTTP** para REST API
- **Amazon SNS** para alertas por email
- **EventBridge** para verificación automática cada 2 horas

👉 [Ver documentación completa del sistema](COMPLETE_SYSTEM_OVERVIEW.md)

## 🏗️ Arquitectura

### Componentes Serverless

- **AWS Lambda**: 8 microservicios Python 3.11
- **Amazon DynamoDB**: 3 tablas con facturación bajo demanda (Pay-per-request)
- **API Gateway HTTP**: API REST económica y serverless
- **Amazon SNS**: Sistema de notificaciones por email
- **EventBridge**: Scheduler para verificación periódica (cada 2 horas)

### Tablas DynamoDB

1. **sensor_data**: Datos de sensores y detección ML
2. **sensor_status**: Estado de sensores y cámaras
3. **alerts**: Historial de alertas enviadas

## 📋 Requisitos Previos

1. **OpenTofu** instalado (versión >= 1.0)
2. **Credenciales AWS** configuradas
3. **Python 3.11** (para desarrollo local opcional)

## 🚀 Despliegue

### 1. Inicializar OpenTofu

```bash
tofu init
```

### 2. Verificar el plan de ejecución

```bash
tofu plan
```

### 3. Aplicar la infraestructura

```bash
tofu apply
```

⚠️ **IMPORTANTE**: Después del despliegue, recibirás emails de confirmación de suscripción SNS en las direcciones configuradas. **Debes confirmar las suscripciones** haciendo clic en los enlaces para recibir alertas.

### 4. Obtener URLs de los endpoints

```bash
tofu output -json
```

## 🔌 API Endpoints

### Servicio 1: Insertar Datos de Sensores
```bash
POST /sensor-data
```
**Body:**
```json
{
  "data": {
    "temperature": "10.12",
    "humidity": "0.18",
    "probability_vapor": "0.11",
    "probability_smug": "0.51",
    "probability_smoke": "0.81",
    "probability_fog": "0.65",
    "alert": "High probability of: SMOKE, SMUG, FOG",
    "danger_alert": ""
  }
}
```

**Comportamiento:**
- Guarda datos en DynamoDB
- Verifica umbrales:
  - Temperatura > 45°C → Alerta
  - Humedad < 10% (0.10) → Alerta
  - Probabilidad humo > 70% (0.70) → Alerta
  - Probabilidad niebla > 60% (0.60) → Alerta CRÍTICA (peligro vial)
- Si se superan umbrales, invoca automáticamente el servicio de alertas

---

### Servicio 2: Insertar Estado de Sensores
```bash
POST /sensor-status
```
**Body:**
```json
{
  "data": {
    "alert": false,
    "status_sensor_humidity": true,
    "status_sensor_temperature": true,
    "status_cameras": [
      {
        "camera": "192.168.2.134",
        "status": true
      }
    ]
  }
}
```

---

### Servicio 3: Enviar Alertas (Manual)
```bash
GET /alerts/send
```
**Body (opcional):**
```json
{
  "alert_type": "GENERAL_ALERT",
  "message": "Custom alert message"
}
```

---

### Servicio 4: Obtener Datos de Sensores
```bash
GET /sensor-data?limit=50&alert_level=DANGER
```
**Query Parameters:**
- `limit`: Número máximo de registros (default: 50)
- `alert_level`: Filtrar por nivel (NORMAL, DANGER)

---

### Servicio 5: Obtener Detección ML
```bash
GET /ml-detection?limit=50&min_probability=0.5
```
**Query Parameters:**
- `limit`: Número máximo de registros (default: 50)
- `min_probability`: Probabilidad mínima de detección (0.0 - 1.0)

---

### Servicio 6: Obtener Alertas
```bash
GET /alerts?limit=100&alert_type=DANGER_THRESHOLD_EXCEEDED
```
**Query Parameters:**
- `limit`: Número máximo de registros (default: 100)
- `alert_type`: Filtrar por tipo de alerta

---

### Servicio 8: Obtener Estado de Sensores
```bash
GET /sensor-status?limit=50&only_problems=false
```
**Query Parameters:**
- `limit`: Número máximo de registros (default: 50)
- `only_problems`: Solo mostrar sensores con problemas (true/false)

---

### Servicio 7: Verificación Automática
Este servicio se ejecuta **automáticamente cada 2 horas** vía EventBridge.
- Verifica el estado de sensores y cámaras
- Envía alertas por email si detecta fallos

## 📧 Sistema de Alertas

### Tipos de Alertas

1. **DANGER_THRESHOLD_EXCEEDED**: Umbrales de peligro superados
2. **SENSOR_MALFUNCTION**: Mal funcionamiento de sensores/cámaras

### Emails Configurados
- santiagovl0308@gmail.com
- jeiboxgmr@gmail.com

## 🔧 Configuración de Variables

Puedes personalizar los umbrales en `variables.tf` o crear un archivo `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
environment = "production"
temperature_threshold = 45
humidity_threshold = 0.10
smoke_probability_threshold = 0.70
fog_probability_threshold = 0.60  # Crítico para seguridad vial
alert_emails = ["email1@example.com", "email2@example.com"]
```

## 📊 Monitoreo

### CloudWatch Logs
Todas las funciones Lambda generan logs en CloudWatch:
- `/aws/lambda/fog-smoke-detection-insert-sensor-data`
- `/aws/lambda/fog-smoke-detection-insert-sensor-status`
- `/aws/lambda/fog-smoke-detection-send-alerts`
- etc.

### Métricas DynamoDB
- Modo serverless (Pay-per-request)
- Point-in-time recovery habilitado
- TTL configurado para limpieza automática

## 🧪 Pruebas

### Ejemplo con curl

```bash
# Obtener la URL del API
API_URL=$(tofu output -raw api_endpoint)

# Insertar datos de sensores
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "50.0",
      "humidity": "0.05",
      "probability_vapor": "0.20",
      "probability_smug": "0.30",
      "probability_smoke": "0.85",
      "alert": "High smoke detected",
      "danger_alert": "Immediate action required"
    }
  }'

# Obtener datos
curl "$API_URL/sensor-data?limit=10"
```

## 💰 Costos Estimados

Esta arquitectura es **100% serverless** con costos basados en uso:

- **Lambda**: Free tier 1M requests/mes
- **DynamoDB**: Pay-per-request (sin capacidad provisionada)
- **API Gateway HTTP**: $1.00 por millón de requests
- **SNS**: $0.50 por millón de requests
- **EventBridge**: $1.00 por millón de eventos

**Estimado mensual para uso moderado**: < $5 USD

## 🗑️ Destruir Infraestructura

```bash
tofu destroy
```

⚠️ Esto eliminará todos los recursos, **incluyendo los datos en DynamoDB**.

## 📝 Estructura del Proyecto

```
API_Cloud/
├── provider.tf           # Configuración de providers
├── variables.tf          # Variables del proyecto
├── dynamodb.tf          # Tablas DynamoDB
├── sns.tf               # Configuración SNS
├── iam.tf               # Roles y políticas IAM
├── lambda.tf            # Funciones Lambda
├── api_gateway.tf       # API Gateway HTTP
├── eventbridge.tf       # Scheduler EventBridge
├── outputs.tf           # Outputs del despliegue
├── lambda_functions/    # Código Python de las funciones
│   ├── insert_sensor_data.py
│   ├── insert_sensor_status.py
│   ├── send_alerts.py
│   ├── get_sensor_data.py
│   ├── get_ml_detection.py
│   ├── get_alerts.py
│   ├── get_sensor_status.py
│   └── check_sensor_status.py
└── README.md
```

## 🔐 Seguridad

- IAM roles con permisos mínimos (least privilege)
- CORS configurado en API Gateway
- Throttling habilitado (50 req/s, burst 100)
- Logs de auditoría en CloudWatch
- Point-in-time recovery en DynamoDB

## 🆘 Troubleshooting

### No recibo emails de alerta
1. Verifica que confirmaste las suscripciones SNS en tu email
2. Revisa CloudWatch Logs de la función `send-alerts`
3. Verifica la configuración del topic SNS en la consola AWS

### Error al desplegar
1. Verifica tus credenciales AWS: `aws sts get-caller-identity`
2. Asegúrate de tener permisos suficientes
3. Revisa los logs: `tofu apply -auto-approve`

### Lambda timeout
- Las funciones tienen timeout de 30s (60s para check_sensor_status)
- Ajusta si necesario en `lambda.tf`

## 📞 Contacto

Para soporte o consultas sobre el proyecto:
- santiagovl0308@gmail.com
- jeiboxgmr@gmail.com
