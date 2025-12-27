# ============================================
# SISTEMA DE DETECCIÓN DE NIEBLA/VAPOR/HUMO
# Infraestructura Cloud Serverless en AWS
# ============================================
#
# Este archivo es el punto de entrada principal
# La configuración está modularizada en varios archivos:
#
# - provider.tf: Configuración de AWS provider
# - variables.tf: Variables del proyecto
# - dynamodb.tf: Tablas DynamoDB
# - sns.tf: Sistema de notificaciones
# - iam.tf: Roles y permisos
# - lambda.tf: Funciones Lambda
# - api_gateway.tf: API Gateway HTTP
# - eventbridge.tf: Scheduler de verificación
# - outputs.tf: Outputs del despliegue

# Los archivos .tf se cargan automáticamente por OpenTofu
# No es necesario declararlos explícitamente aquí

# Para desplegar:
#   1. tofu init
#   2. tofu plan
#   3. tofu apply
#
# O usa el script automatizado:
#   ./deploy.sh
