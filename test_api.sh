#!/bin/bash

# Script de pruebas para el Sistema de Detección
# Prueba todos los endpoints del API

set -e

echo "=========================================="
echo "  Pruebas del Sistema de Detección       "
echo "=========================================="
echo ""

# Obtener API endpoint
if [ ! -f "deployment_info.txt" ]; then
    echo "Error: No se encontró deployment_info.txt"
    echo "Ejecuta primero ./deploy.sh"
    exit 1
fi

API_URL=$(tofu output -raw api_endpoint)
echo "API Endpoint: $API_URL"
echo ""

# Test 1: Insertar datos de sensores (datos normales)
echo "Test 1: Insertar datos normales de sensores"
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "25.5",
      "humidity": "0.65",
      "probability_vapor": "0.20",
      "probability_smug": "0.15",
      "probability_smoke": "0.10",
      "probability_fog": "0.25",
      "alert": "Normal conditions",
      "danger_alert": ""
    }
  }' | jq
echo ""
echo "----------------------------------------"

# Test 2: Insertar datos de sensores (con alerta)
echo "Test 2: Insertar datos con alertas (umbrales superados)"
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "50.0",
      "humidity": "0.08",
      "probability_vapor": "0.20",
      "probability_smug": "0.40",
      "probability_smoke": "0.85",
      "probability_fog": "0.30",
      "alert": "High smoke and temperature detected",
      "danger_alert": "Immediate action required"
    }
  }' | jq
echo ""
echo "----------------------------------------"

# Test 2.5: Insertar datos con NIEBLA ALTA (CRÍTICO para conducción)
echo "Test 2.5: Insertar datos con ALTA NIEBLA - Peligro Vial"
curl -X POST "$API_URL/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": "18.0",
      "humidity": "0.88",
      "probability_vapor": "0.35",
      "probability_smug": "0.30",
      "probability_smoke": "0.20",
      "probability_fog": "0.85",
      "alert": "CRITICAL: HIGH FOG DETECTED - DRIVING HAZARD!",
      "danger_alert": "Severe visibility reduction on roads"
    }
  }' | jq
echo ""
echo "----------------------------------------"

# Test 3: Insertar estado de sensores
echo "Test 3: Insertar estado de sensores"
curl -X POST "$API_URL/sensor-status" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "alert": false,
      "status_sensor_humidity": true,
      "status_sensor_temperature": true,
      "status_cameras": [
        {
          "camera": "192.168.2.134",
          "status": true
        },
        {
          "camera": "192.168.2.135",
          "status": true
        }
      ]
    }
  }' | jq
echo ""
echo "----------------------------------------"

# Esperar un poco para que se procesen los datos
echo "Esperando 3 segundos..."
sleep 3

# Test 4: Obtener datos de sensores
echo "Test 4: Obtener datos de sensores"
curl "$API_URL/sensor-data?limit=5" | jq
echo ""
echo "----------------------------------------"

# Test 5: Obtener datos de detección ML
echo "Test 5: Obtener datos de detección ML"
curl "$API_URL/ml-detection?limit=5" | jq
echo ""
echo "----------------------------------------"

# Test 6: Obtener alertas
echo "Test 6: Obtener alertas"
curl "$API_URL/alerts?limit=10" | jq
echo ""
echo "----------------------------------------"

# Test 7: Obtener estado de sensores
echo "Test 7: Obtener estado de sensores"
curl "$API_URL/sensor-status?limit=5" | jq
echo ""
echo "----------------------------------------"

# Test 8: Filtrar por nivel de alerta
echo "Test 8: Obtener solo registros con DANGER"
curl "$API_URL/sensor-data?limit=10&alert_level=DANGER" | jq
echo ""
echo "----------------------------------------"

echo ""
echo "=========================================="
echo "  Pruebas completadas                    "
echo "=========================================="
echo ""
echo "Notas:"
echo "  - Revisa tu email para alertas de umbrales superados"
echo "  - El Test 2 debió generar una alerta automática"
echo "  - El servicio de verificación se ejecuta cada 2 horas"
echo ""
