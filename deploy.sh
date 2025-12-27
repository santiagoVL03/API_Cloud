#!/bin/bash

# Script de despliegue automatizado para el Sistema de Detección
# Fog/Smoke en AWS usando OpenTofu

set -e  # Salir si hay errores

echo "=================================================="
echo "   Sistema de Detección de Niebla/Vapor/Humo    "
echo "       Despliegue de Infraestructura Cloud       "
echo "=================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que OpenTofu está instalado
if ! command -v tofu &> /dev/null; then
    print_error "OpenTofu no está instalado"
    echo "Instala OpenTofu desde: https://opentofu.org/docs/intro/install/"
    exit 1
fi

print_info "OpenTofu versión: $(tofu version | head -n 1)"

# Verificar credenciales AWS
print_info "Verificando credenciales AWS..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "No se detectaron credenciales AWS válidas"
    echo "Configura tus credenciales con: aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)
print_info "AWS Account: ${AWS_ACCOUNT}"
print_info "AWS Region: ${AWS_REGION:-us-east-1}"
echo ""

# Inicializar OpenTofu
print_info "Inicializando OpenTofu..."
tofu init
echo ""

# Validar configuración
print_info "Validando configuración..."
tofu validate
echo ""

# Mostrar plan
print_info "Generando plan de ejecución..."
tofu plan -out=tfplan
echo ""

# Preguntar confirmación
print_warning "¿Deseas aplicar este plan? (yes/no)"
read -p "Respuesta: " confirmation

if [ "$confirmation" != "yes" ]; then
    print_info "Despliegue cancelado"
    exit 0
fi

# Aplicar infraestructura
print_info "Desplegando infraestructura en AWS..."
tofu apply tfplan
echo ""

# Mostrar outputs
print_info "=================================================="
print_info "           DESPLIEGUE COMPLETADO                 "
print_info "=================================================="
echo ""

print_info "API Endpoint:"
API_ENDPOINT=$(tofu output -raw api_endpoint)
echo "  ${API_ENDPOINT}"
echo ""

print_info "Endpoints disponibles:"
echo "  POST ${API_ENDPOINT}/sensor-data         - Insertar datos de sensores"
echo "  POST ${API_ENDPOINT}/sensor-status       - Insertar estado de sensores"
echo "  GET  ${API_ENDPOINT}/alerts/send         - Enviar alerta manual"
echo "  GET  ${API_ENDPOINT}/sensor-data         - Obtener datos de sensores"
echo "  GET  ${API_ENDPOINT}/ml-detection        - Obtener detección ML"
echo "  GET  ${API_ENDPOINT}/alerts              - Obtener alertas"
echo "  GET  ${API_ENDPOINT}/sensor-status       - Obtener estado de sensores"
echo ""

print_warning "=================================================="
print_warning "           ACCIÓN REQUERIDA                      "
print_warning "=================================================="
echo ""
print_warning "Se han enviado emails de confirmación a:"
tofu output -json alert_email_addresses | jq -r '.[]' | while read email; do
    echo "  - ${email}"
done
echo ""
print_warning "Debes confirmar las suscripciones SNS haciendo clic"
print_warning "en los enlaces de los emails para recibir alertas."
echo ""

print_info "Para ver todos los outputs:"
echo "  tofu output -json | jq"
echo ""

print_info "Para destruir la infraestructura:"
echo "  tofu destroy"
echo ""

# Guardar información importante
print_info "Guardando información de despliegue..."
cat > deployment_info.txt <<EOF
=== Información de Despliegue ===
Fecha: $(date)
AWS Account: ${AWS_ACCOUNT}
AWS Region: ${AWS_REGION:-us-east-1}

API Endpoint: ${API_ENDPOINT}

Endpoints:
  POST ${API_ENDPOINT}/sensor-data
  POST ${API_ENDPOINT}/sensor-status
  GET  ${API_ENDPOINT}/alerts/send
  GET  ${API_ENDPOINT}/sensor-data
  GET  ${API_ENDPOINT}/ml-detection
  GET  ${API_ENDPOINT}/alerts
  GET  ${API_ENDPOINT}/sensor-status

DynamoDB Tables:
$(tofu output -json dynamodb_tables | jq -r 'to_entries[] | "  - \(.key): \(.value)"')

Lambda Functions:
$(tofu output -json lambda_functions | jq -r 'to_entries[] | "  - \(.key): \(.value)"')

SNS Topic ARN:
$(tofu output -raw sns_topic_arn)

Verificación de sensores:
  Cada 2 horas automáticamente
EOF

print_info "Información guardada en: deployment_info.txt"
echo ""

print_info "¡Despliegue completado exitosamente! 🚀"
