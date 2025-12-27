# 🚀 Inicio Rápido - Sistema de Detección Serverless

## ⚡ Despliegue en 3 Pasos

### 1️⃣ Verificar Requisitos

```bash
# Verificar OpenTofu
tofu version

# Verificar AWS CLI y credenciales
aws sts get-caller-identity

# Si no tienes credenciales configuradas:
aws configure
```

### 2️⃣ Desplegar Infraestructura

```bash
cd /home/santiagouwu/Documents/University/API_Cloud

# Opción A: Script automatizado (RECOMENDADO)
./deploy.sh

# Opción B: Manual
tofu init
tofu plan
tofu apply
```

⏱️ **Tiempo estimado:** 3-5 minutos

### 3️⃣ Confirmar Suscripciones Email

Después del despliegue, recibirás 2 emails:
- ✉️ santiagovl0308@gmail.com
- ✉️ jeiboxgmr@gmail.com

**¡IMPORTANTE!** Haz clic en "Confirm subscription" en ambos emails.

---

## 🧪 Probar la API

### Opción 1: Script de Pruebas Automatizado

```bash
./test_api.sh
```

### Opción 2: Prueba Manual Rápida

```bash
# Obtener URL del API
export API_URL=$(tofu output -raw api_endpoint)

# Enviar datos de prueba
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "25.0",
      "humidity": "0.60",
      "probability_vapor": "0.15",
      "probability_smug": "0.10",
      "probability_smoke": "0.05",
      "probability_fog": "0.30",
      "alert": "Test desde Fog API",
      "danger_alert": ""
    }
  }'

# Ver los datos insertados
curl "$API_URL/sensor-data?limit=5" | jq
```

---

## 📋 Información del Despliegue

### Ver URLs y Recursos

```bash
# Ver todos los outputs
tofu output

# URL del API
tofu output api_endpoint

# Todos los endpoints
tofu output -json endpoints | jq

# Tablas DynamoDB
tofu output -json dynamodb_tables | jq

# Funciones Lambda
tofu output -json lambda_functions | jq
```

### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/sensor-data` | Insertar datos de sensores |
| POST | `/sensor-status` | Insertar estado de sensores |
| GET | `/sensor-data` | Obtener datos de sensores |
| GET | `/ml-detection` | Obtener detección ML |
| GET | `/alerts` | Obtener historial de alertas |
| GET | `/sensor-status` | Obtener estado de sensores |
| GET | `/alerts/send` | Enviar alerta manual |

---

## 🔍 Monitoreo

### Ver Logs de Lambda

```bash
# Listar todos los grupos de logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/fog-smoke-detection

# Ver logs de inserción de datos
aws logs tail /aws/lambda/fog-smoke-detection-insert-sensor-data --follow

# Ver logs de alertas
aws logs tail /aws/lambda/fog-smoke-detection-send-alerts --follow
```

### Consola Web AWS

1. **Lambda Functions:** https://console.aws.amazon.com/lambda
2. **DynamoDB Tables:** https://console.aws.amazon.com/dynamodb
3. **API Gateway:** https://console.aws.amazon.com/apigateway
4. **CloudWatch Logs:** https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups

---

## 🎯 Integración con tu API Fog

### Python Example

```python
import requests
import json

# Tu API Cloud
CLOUD_API = "https://YOUR_API_URL.execute-api.us-east-1.amazonaws.com"

def send_to_cloud(sensor_data):
    """Enviar datos desde Fog Computing a Cloud"""
    
    payload = {
        "data": {
            "temperature": str(sensor_data['temp']),
            "humidity": str(sensor_data['humidity']),
            "probability_vapor": str(sensor_data['vapor']),
            "probability_smug": str(sensor_data['smug']),
            "probability_smoke": str(sensor_data['smoke']),
            "probability_fog": str(sensor_data['fog']),
            "alert": sensor_data.get('alert', ''),
            "danger_alert": sensor_data.get('danger_alert', '')
        }
    }
    
    try:
        response = requests.post(
            f"{CLOUD_API}/sensor-data",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending to cloud: {e}")
        return None

# Ejemplo de uso
data = {
    'temp': 28.5,
    'humidity': 0.65,
    'vapor': 0.20,
    'smug': 0.15,
    'smoke': 0.10,
    'fog': 0.35,
    'alert': 'Normal reading'
}

result = send_to_cloud(data)
print(f"Cloud response: {result}")
```

### Node.js Example

```javascript
const axios = require('axios');

const CLOUD_API = 'https://YOUR_API_URL.execute-api.us-east-1.amazonaws.com';

async function sendToCloud(sensorData) {
    const payload = {
        data: {
            temperature: sensorData.temp.toString(),
            humidity: sensorData.humidity.toString(),
            probability_vapor: sensorData.vapor.toString(),
            probability_smug: sensorData.smug.toString(),
            probability_smoke: sensorData.smoke.toString(),
            probability_fog: sensorData.fog.toString(),
            alert: sensorData.alert || '',
            danger_alert: sensorData.danger_alert || ''
        }
    };
    
    try {
        const response = await axios.post(
            `${CLOUD_API}/sensor-data`,
            payload,
            { timeout: 10000 }
        );
        return response.data;
    } catch (error) {
        console.error('Error sending to cloud:', error);
        return null;
    }
}

// Ejemplo de uso
const data = {
    temp: 28.5,
    humidity: 0.65,
    vapor: 0.20,
    smug: 0.15,
    smoke: 0.10,
    fog: 0.35,
    alert: 'Normal reading'
};

sendToCloud(data).then(result => {
    console.log('Cloud response:', result);
});
```

---

## 🔧 Configuración Avanzada

### Cambiar Umbrales de Alerta

Edita `terraform.tfvars`:
```hcl
temperature_threshold = 50        # Cambiar temperatura crítica
humidity_threshold = 0.08         # Cambiar humedad crítica
smoke_probability_threshold = 0.75 # Cambiar probabilidad humo crítica
```

Aplica cambios:
```bash
tofu apply
```

### Agregar Más Emails

Edita `terraform.tfvars`:
```hcl
alert_emails = [
  "santiagovl0308@gmail.com",
  "jeiboxgmr@gmail.com",
  "nuevo@email.com"
]
```

Aplica cambios:
```bash
tofu apply
```

### Cambiar Frecuencia de Verificación

Edita `eventbridge.tf`, línea con `schedule_expression`:
```hcl
# Cada 1 hora
schedule_expression = "rate(1 hour)"

# Cada 30 minutos
schedule_expression = "rate(30 minutes)"

# Cada día a las 9 AM
schedule_expression = "cron(0 9 * * ? *)"
```

---

## 🗑️ Limpieza y Destrucción

### Eliminar Toda la Infraestructura

```bash
# ADVERTENCIA: Esto eliminará TODOS los recursos y datos
tofu destroy

# Confirma escribiendo: yes
```

**Recursos que se eliminarán:**
- ✗ 8 funciones Lambda
- ✗ 3 tablas DynamoDB (incluyendo todos los datos)
- ✗ API Gateway
- ✗ Tópico SNS
- ✗ Roles IAM
- ✗ EventBridge rules
- ✗ CloudWatch logs

---

## ❓ Troubleshooting Rápido

### No recibo emails

```bash
# Verificar suscripciones SNS
aws sns list-subscriptions-by-topic \
  --topic-arn $(tofu output -raw sns_topic_arn)

# Si aparece "PendingConfirmation", confirma el email
```

### Error al hacer POST

```bash
# Verificar que el endpoint existe
curl -I "$API_URL/sensor-data"

# Debería retornar: HTTP/2 200 (con método GET)
# o error 404 si no existe
```

### Ver errores en Lambda

```bash
# Ver últimos errores
aws logs filter-log-events \
  --log-group-name /aws/lambda/fog-smoke-detection-insert-sensor-data \
  --filter-pattern "ERROR" \
  --max-items 10
```

### DynamoDB no guarda datos

```bash
# Verificar que la tabla existe
aws dynamodb describe-table \
  --table-name fog-smoke-detection-sensor-data

# Contar items en la tabla
aws dynamodb scan \
  --table-name fog-smoke-detection-sensor-data \
  --select "COUNT"
```

---

## 📚 Documentación Completa

- **README.md** - Documentación general
- **ARCHITECTURE.md** - Diagrama y arquitectura detallada
- **EXAMPLES.md** - Ejemplos de uso de todos los endpoints
- **deployment_info.txt** - Info generada después del despliegue

---

## 💰 Costos Estimados

Con uso moderado (1000 requests/día):

| Servicio | Costo Mensual |
|----------|---------------|
| Lambda (8 funciones) | ~$0.20 |
| DynamoDB (Pay-per-request) | ~$1.50 |
| API Gateway HTTP | ~$1.00 |
| SNS | ~$0.10 |
| EventBridge | ~$0.01 |
| **TOTAL** | **~$2.81/mes** |

🎉 **Free Tier:** Los primeros meses pueden ser GRATIS

---

## ✅ Checklist Post-Despliegue

- [ ] Infraestructura desplegada exitosamente
- [ ] Emails de SNS confirmados (ambos)
- [ ] API probada con curl o test script
- [ ] Logs de CloudWatch verificados
- [ ] URL del API guardada en tu Fog API
- [ ] Documentación leída
- [ ] Umbrales configurados según necesidades

---

## 🎓 Siguientes Pasos

1. **Integrar con tu API Fog Computing**
   - Usa los ejemplos de Python/Node.js
   - Envía datos cada X segundos/minutos

2. **Configurar Monitoreo**
   - CloudWatch Dashboards
   - Alarmas personalizadas

3. **Optimizar Costos**
   - Revisar métricas de uso
   - Ajustar TTL en DynamoDB

4. **Extender Funcionalidad**
   - Agregar más sensores
   - Nuevos tipos de alertas
   - Dashboard web

---

## 📞 Soporte

**Emails:**
- santiagovl0308@gmail.com
- jeiboxgmr@gmail.com

**Documentación AWS:**
- [Lambda](https://docs.aws.amazon.com/lambda/)
- [DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [API Gateway](https://docs.aws.amazon.com/apigateway/)

---

**🎉 ¡Disfruta tu sistema serverless de detección!**
