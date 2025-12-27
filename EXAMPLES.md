# Ejemplos de Uso de la API

Este documento contiene ejemplos prácticos de cómo usar todos los endpoints del sistema.

## Configuración Inicial

Obtén la URL de tu API:
```bash
cd /home/santiagouwu/Documents/University/API_Cloud
export API_URL=$(tofu output -raw api_endpoint)
echo $API_URL
```

## 📤 Endpoints POST

### 1. Insertar Datos de Sensores

**Endpoint:** `POST /sensor-data`

**Caso 1: Condiciones Normales**
```bash
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "22.5",
      "humidity": "0.65",
      "probability_vapor": "0.15",
      "probability_smug": "0.10",
      "probability_smoke": "0.05",
      "probability_fog": "0.20",
      "alert": "Normal conditions",
      "danger_alert": ""
    }
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Data inserted successfully",
  "record_id": "abc123...",
  "timestamp": "2025-12-27T10:30:00.123456",
  "alert_level": "NORMAL",
  "danger_conditions": []
}
```

**Caso 2: Temperatura Alta (generará alerta)**
```bash
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "52.0",
      "humidity": "0.45",
      "probability_vapor": "0.30",
      "probability_smug": "0.25",
      "probability_smoke": "0.15",
      "probability_fog": "0.10",
      "alert": "High temperature detected",
      "danger_alert": "Check cooling systems"
    }
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Data inserted successfully",
  "record_id": "def456...",
  "timestamp": "2025-12-27T10:35:00.123456",
  "alert_level": "DANGER",
  "danger_conditions": ["High temperature: 52.0°C"]
}
```
🔔 **Se enviará un email automáticamente**

**Caso 3: Alta Niebla + Humo (CRÍTICO para conducción)**
```bash
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "18.0",
      "humidity": "0.85",
      "probability_vapor": "0.30",
      "probability_smug": "0.40",
      "probability_smoke": "0.75",
      "probability_fog": "0.80",
      "alert": "High probability of: FOG and SMOKE - DRIVING HAZARD!",
      "danger_alert": "Severe visibility reduction - Road safety alert"
    }
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Data inserted successfully",
  "record_id": "ghi789...",
  "timestamp": "2025-12-27T10:40:00.123456",
  "alert_level": "DANGER",
  "danger_conditions": [
    "High smoke probability: 75.0%",
    "HIGH FOG DETECTED: 80.0% - DRIVING HAZARD!"
  ]
}
```
🔔 **Se enviará un email automáticamente con PRIORIDAD ALTA por peligro vial**

---

**Caso 4: Solo Humedad Baja**
```bash
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "35.0",
      "humidity": "0.08",
      "probability_vapor": "0.10",
      "probability_smug": "0.40",
      "probability_smoke": "0.20",
      "probability_fog": "0.15",
      "alert": "Low humidity detected",
      "danger_alert": ""
    }
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Data inserted successfully",
  "record_id": "ghi789...",
  "timestamp": "2025-12-27T10:40:00.123456",
  "alert_level": "DANGER",
  "danger_conditions": [
    "Low humidity: 8.0%",
    "High smoke probability: 85.0%"
  ]
}
```
🔔 **Se enviará un email automáticamente**

---

### 2. Insertar Estado de Sensores

**Endpoint:** `POST /sensor-status`

**Caso 1: Todo Funcionando**
```bash
curl -X POST "$API_URL/sensor-status" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "alert": false,
      "status_sensor_humidity": true,
      "status_sensor_temperature": true,
      "status_cameras": [
        {"camera": "192.168.2.134", "status": true},
        {"camera": "192.168.2.135", "status": true},
        {"camera": "192.168.2.136", "status": true}
      ]
    }
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Sensor status inserted successfully",
  "record_id": "jkl012...",
  "timestamp": "2025-12-27T10:45:00.123456",
  "has_alert": "false",
  "sensors_ok": true,
  "cameras_ok": true
}
```

**Caso 2: Sensor de Humedad con Fallo**
```bash
curl -X POST "$API_URL/sensor-status" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "alert": true,
      "status_sensor_humidity": false,
      "status_sensor_temperature": true,
      "status_cameras": [
        {"camera": "192.168.2.134", "status": true},
        {"camera": "192.168.2.135", "status": true}
      ]
    }
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Sensor status inserted successfully",
  "record_id": "mno345...",
  "timestamp": "2025-12-27T10:50:00.123456",
  "has_alert": "true",
  "sensors_ok": false,
  "cameras_ok": true
}
```

**Caso 3: Cámara Desconectada**
```bash
curl -X POST "$API_URL/sensor-status" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "alert": true,
      "status_sensor_humidity": true,
      "status_sensor_temperature": true,
      "status_cameras": [
        {"camera": "192.168.2.134", "status": true},
        {"camera": "192.168.2.135", "status": false},
        {"camera": "192.168.2.136", "status": true}
      ]
    }
  }'
```

---

## 📥 Endpoints GET

### 3. Obtener Datos de Sensores

**Endpoint:** `GET /sensor-data`

**Obtener últimos 10 registros:**
```bash
curl "$API_URL/sensor-data?limit=10"
```

**Filtrar solo registros con DANGER:**
```bash
curl "$API_URL/sensor-data?limit=20&alert_level=DANGER"
```

**Filtrar solo registros NORMAL:**
```bash
curl "$API_URL/sensor-data?limit=20&alert_level=NORMAL"
```

**Respuesta esperada:**
```json
{
  "count": 10,
  "data": [
    {
      "id": "abc123...",
      "timestamp": "2025-12-27T10:40:00.123456",
      "temperature": 35.0,
      "humidity": 0.08,
      "probability_vapor": 0.10,
      "probability_smug": 0.40,
      "probability_smoke": 0.85,
      "alert": "High probability of: SMOKE, SMUG",
      "danger_alert": "Potential fire hazard",
      "alert_level": "DANGER",
      "danger_conditions": ["Low humidity: 8.0%", "High smoke probability: 85.0%"]
    }
  ]
}
```

---

### 4. Obtener Detección ML

**Endpoint:** `GET /ml-detection`

**Obtener últimas 15 detecciones:**
```bash
curl "$API_URL/ml-detection?limit=15"
```

**Filtrar detecciones con probabilidad > 50%:**
```bash
curl "$API_URL/ml-detection?limit=20&min_probability=0.5"
```

**Respuesta esperada:**
```json
{
  "count": 15,
  "data": [
    {
      "id": "abc123...",
      "timestamp": "2025-12-27T10:40:00.123456",
      "detection": {
        "vapor": 0.10,
        "smug": 0.40,
        "smoke": 0.85
      },
      "alert": "High probability of: SMOKE, SMUG",
      "danger_alert": "Potential fire hazard",
      "alert_level": "DANGER"
    }
  ]
}
```

---

### 5. Obtener Alertas

**Endpoint:** `GET /alerts`

**Obtener últimas 20 alertas:**
```bash
curl "$API_URL/alerts?limit=20"
```

**Filtrar por tipo de alerta:**
```bash
curl "$API_URL/alerts?limit=50&alert_type=DANGER_THRESHOLD_EXCEEDED"
```

**Respuesta esperada:**
```json
{
  "count": 20,
  "alerts": [
    {
      "alert_id": "xyz789...",
      "timestamp": "2025-12-27T10:40:15.123456",
      "type": "EMAIL_ALERT",
      "alert_type": "DANGER_THRESHOLD_EXCEEDED",
      "status": "sent",
      "sns_message_id": "abc-123..."
    },
    {
      "alert_id": "ghi789...",
      "timestamp": "2025-12-27T10:40:00.123456",
      "type": "DANGER_DETECTION",
      "alert_level": "DANGER",
      "alert": "High probability of: SMOKE, SMUG",
      "danger_conditions": ["Low humidity: 8.0%", "High smoke probability: 85.0%"],
      "temperature": 35.0,
      "humidity": 0.08,
      "probability_smoke": 0.85
    }
  ]
}
```

---

### 6. Obtener Estado de Sensores

**Endpoint:** `GET /sensor-status`

**Obtener últimos 10 estados:**
```bash
curl "$API_URL/sensor-status?limit=10"
```

**Obtener solo sensores con problemas:**
```bash
curl "$API_URL/sensor-status?limit=20&only_problems=true"
```

**Respuesta esperada:**
```json
{
  "count": 10,
  "latest_status": {
    "id": "mno345...",
    "timestamp": "2025-12-27T10:50:00.123456",
    "alert": true,
    "has_alert": "true",
    "status_sensor_humidity": false,
    "status_sensor_temperature": true,
    "status_cameras": [
      {"camera": "192.168.2.134", "status": true},
      {"camera": "192.168.2.135", "status": true}
    ],
    "sensors_ok": false,
    "cameras_ok": true,
    "all_systems_operational": false
  },
  "history": [...]
}
```

---

### 7. Enviar Alerta Manual

**Endpoint:** `GET /alerts/send`

**Enviar alerta personalizada:**
```bash
curl -X GET "$API_URL/alerts/send" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "MANUAL_TEST",
    "message": "Prueba manual del sistema de alertas"
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Alert sent successfully",
  "alert_id": "pqr678...",
  "sns_message_id": "def-456...",
  "timestamp": "2025-12-27T11:00:00.123456"
}
```

---

## 🤖 Proceso Automático

### Verificación de Sensores (Cada 2 horas)

Esta función se ejecuta automáticamente. No requiere invocación manual.

**Comportamiento:**
1. Se ejecuta automáticamente cada 2 horas
2. Consulta el estado más reciente de sensores
3. Si encuentra sensores o cámaras con `status: false`:
   - Genera un email de alerta
   - Envía vía SNS
   - Registra en tabla de alertas

**Email enviado incluye:**
- Lista de sensores con problemas
- Lista de cámaras desconectadas
- Timestamp del problema
- ID de alerta para seguimiento

---

## 📊 Ejemplos con Python

### Script de Integración

```python
import requests
import json

API_URL = "https://YOUR_API_URL.execute-api.us-east-1.amazonaws.com"

def send_sensor_data(temp, humidity, vapor, smug, smoke):
    """Enviar datos de sensores"""
    endpoint = f"{API_URL}/sensor-data"
    
    payload = {
        "data": {
            "temperature": str(temp),
            "humidity": str(humidity),
            "probability_vapor": str(vapor),
            "probability_smug": str(smug),
            "probability_smoke": str(smoke),
            "alert": f"Readings: T={temp}°C, H={humidity*100}%",
            "danger_alert": ""
        }
    }
    
    response = requests.post(endpoint, json=payload)
    return response.json()

def get_latest_data(limit=10):
    """Obtener últimos datos"""
    endpoint = f"{API_URL}/sensor-data?limit={limit}"
    response = requests.get(endpoint)
    return response.json()

def get_danger_alerts():
    """Obtener solo alertas de peligro"""
    endpoint = f"{API_URL}/sensor-data?alert_level=DANGER&limit=50"
    response = requests.get(endpoint)
    return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    # Enviar datos normales
    result = send_sensor_data(
        temp=25.5,
        humidity=0.65,
        vapor=0.15,
        smug=0.10,
        smoke=0.05
    )
    print(f"Resultado: {result}")
    
    # Enviar datos críticos
    result = send_sensor_data(
        temp=50.0,
        humidity=0.08,
        vapor=0.20,
        smug=0.45,
        smoke=0.88
    )
    print(f"Alerta generada: {result}")
    
    # Obtener datos recientes
    data = get_latest_data(5)
    print(f"Últimos 5 registros: {json.dumps(data, indent=2)}")
```

---

## 🔍 Pruebas de Carga

### Test con múltiples requests

```bash
# Enviar 10 requests en paralelo
for i in {1..10}; do
  curl -X POST "$API_URL/sensor-data" \
    -H "Content-Type: application/json" \
    -d "{
      \"data\": {
        \"temperature\": \"$((20 + RANDOM % 30))\",
        \"humidity\": \"0.$((RANDOM % 100))\",
        \"probability_vapor\": \"0.$((RANDOM % 100))\",
        \"probability_smug\": \"0.$((RANDOM % 100))\",
        \"probability_smoke\": \"0.$((RANDOM % 100))\",
        \"alert\": \"Test $i\",
        \"danger_alert\": \"\"
      }
    }" &
done
wait
echo "Test completado"
```

---

## 📧 Formato de Emails

### Email de Umbral Superado

```
╔════════════════════════════════════════════════════════════╗
║   SISTEMA DE DETECCIÓN DE NIEBLA/VAPOR/HUMO - ALERTA     ║
╚════════════════════════════════════════════════════════════╝

⚠️  ALERTA CRÍTICA DETECTADA
Fecha y Hora: 2025-12-27T10:40:00.123456
ID de Alerta: abc123...

🔴 CONDICIONES PELIGROSAS DETECTADAS:
  • Low humidity: 8.0%
  • High smoke probability: 85.0%

📊 DATOS DE SENSORES:
  • Temperatura: 35.0°C
  • Humedad: 8.0%
  • Probabilidad de Humo: 85.0%

📢 ALERTAS DEL SISTEMA:
  High probability of: SMOKE, SMUG

⚡ ACCIÓN REQUERIDA:
  Se recomienda verificar inmediatamente el área monitoreada
  y tomar las medidas de seguridad correspondientes.
```

### Email de Fallo de Sensores

```
╔════════════════════════════════════════════════════════════╗
║   SISTEMA DE DETECCIÓN - FALLO DE SENSORES               ║
╚════════════════════════════════════════════════════════════╝

⚠️  ALERTA DE MANTENIMIENTO
Fecha y Hora: 2025-12-27T12:00:00.123456
ID de Alerta: xyz789...

🔧 SENSORES CON PROBLEMAS:
  • Sensor de Humedad

📹 CÁMARAS CON PROBLEMAS:
  • Cámara: 192.168.2.135

⚡ ACCIÓN REQUERIDA:
  Se requiere revisión técnica del equipamiento reportado
  para restaurar la funcionalidad completa del sistema.
```
