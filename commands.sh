#!/bin/bash
# Comandos útiles para gestionar la infraestructura

# ============================================
# COMANDOS DE DESPLIEGUE
# ============================================

# Inicializar OpenTofu
alias tofu-init='tofu init'

# Ver plan sin aplicar
alias tofu-plan='tofu plan'

# Aplicar cambios
alias tofu-apply='tofu apply'

# Ver estado actual
alias tofu-show='tofu show'

# Ver outputs
alias tofu-output='tofu output -json | jq'

# ============================================
# COMANDOS DE API
# ============================================

# Obtener URL del API
export API_URL=$(tofu output -raw api_endpoint 2>/dev/null || echo "Run tofu apply first")

# Enviar datos de prueba
alias api-test-normal='curl -X POST "$API_URL/sensor-data" -H "Content-Type: application/json" -d "{\"data\":{\"temperature\":\"25.0\",\"humidity\":\"0.65\",\"probability_vapor\":\"0.15\",\"probability_smug\":\"0.10\",\"probability_smoke\":\"0.05\",\"alert\":\"Normal\",\"danger_alert\":\"\"}}"'

# Enviar datos con alerta
alias api-test-danger='curl -X POST "$API_URL/sensor-data" -H "Content-Type: application/json" -d "{\"data\":{\"temperature\":\"50.0\",\"humidity\":\"0.08\",\"probability_vapor\":\"0.20\",\"probability_smug\":\"0.40\",\"probability_smoke\":\"0.85\",\"alert\":\"Danger\",\"danger_alert\":\"Critical\"}}"'

# Ver últimos datos
alias api-get-data='curl "$API_URL/sensor-data?limit=5" | jq'

# Ver solo peligros
alias api-get-danger='curl "$API_URL/sensor-data?alert_level=DANGER&limit=10" | jq'

# Ver alertas
alias api-get-alerts='curl "$API_URL/alerts?limit=10" | jq'

# Ver estado de sensores
alias api-get-status='curl "$API_URL/sensor-status?limit=5" | jq'

# ============================================
# COMANDOS DE MONITOREO
# ============================================

# Ver logs de inserción de datos
alias logs-insert='aws logs tail /aws/lambda/fog-smoke-detection-insert-sensor-data --follow'

# Ver logs de alertas
alias logs-alerts='aws logs tail /aws/lambda/fog-smoke-detection-send-alerts --follow'

# Ver logs de verificación
alias logs-check='aws logs tail /aws/lambda/fog-smoke-detection-check-sensor-status --follow'

# Ver todos los grupos de logs
alias logs-list='aws logs describe-log-groups --log-group-name-prefix /aws/lambda/fog-smoke-detection'

# ============================================
# COMANDOS DE DYNAMODB
# ============================================

# Contar items en sensor_data
alias db-count-data='aws dynamodb scan --table-name fog-smoke-detection-sensor-data --select "COUNT"'

# Contar items en sensor_status
alias db-count-status='aws dynamodb scan --table-name fog-smoke-detection-sensor-status --select "COUNT"'

# Contar items en alerts
alias db-count-alerts='aws dynamodb scan --table-name fog-smoke-detection-alerts --select "COUNT"'

# Ver últimos 5 items de sensor_data
alias db-last-data='aws dynamodb scan --table-name fog-smoke-detection-sensor-data --limit 5'

# ============================================
# COMANDOS DE SNS
# ============================================

# Ver suscripciones SNS
alias sns-subs='aws sns list-subscriptions-by-topic --topic-arn $(tofu output -raw sns_topic_arn 2>/dev/null)'

# Enviar alerta de prueba
alias sns-test='aws sns publish --topic-arn $(tofu output -raw sns_topic_arn 2>/dev/null) --subject "Test Alert" --message "This is a test alert from the fog-smoke detection system"'

# ============================================
# COMANDOS DE LIMPIEZA
# ============================================

# Limpiar archivos temporales
alias clean-temp='rm -rf .terraform/lambda_zips/*.zip'

# Destruir toda la infraestructura (CUIDADO!)
alias tofu-destroy='tofu destroy'

# ============================================
# AYUDA
# ============================================

show_help() {
    echo "=========================================="
    echo "  Comandos Útiles - Fog Smoke Detection  "
    echo "=========================================="
    echo ""
    echo "DESPLIEGUE:"
    echo "  tofu-init          - Inicializar OpenTofu"
    echo "  tofu-plan          - Ver plan de cambios"
    echo "  tofu-apply         - Aplicar infraestructura"
    echo "  tofu-output        - Ver outputs en JSON"
    echo ""
    echo "API TESTING:"
    echo "  api-test-normal    - Enviar datos normales"
    echo "  api-test-danger    - Enviar datos con alerta"
    echo "  api-get-data       - Ver últimos 5 datos"
    echo "  api-get-danger     - Ver solo alertas DANGER"
    echo "  api-get-alerts     - Ver historial de alertas"
    echo "  api-get-status     - Ver estado de sensores"
    echo ""
    echo "MONITOREO:"
    echo "  logs-insert        - Ver logs de inserción (live)"
    echo "  logs-alerts        - Ver logs de alertas (live)"
    echo "  logs-check         - Ver logs de verificación (live)"
    echo "  logs-list          - Listar todos los logs"
    echo ""
    echo "DYNAMODB:"
    echo "  db-count-data      - Contar registros en sensor_data"
    echo "  db-count-status    - Contar registros en sensor_status"
    echo "  db-count-alerts    - Contar registros en alerts"
    echo "  db-last-data       - Ver últimos 5 registros"
    echo ""
    echo "SNS:"
    echo "  sns-subs           - Ver suscripciones de email"
    echo "  sns-test           - Enviar email de prueba"
    echo ""
    echo "LIMPIEZA:"
    echo "  clean-temp         - Limpiar archivos temporales"
    echo "  tofu-destroy       - Destruir infraestructura (CUIDADO!)"
    echo ""
    echo "Para usar estos comandos, ejecuta:"
    echo "  source ./commands.sh"
    echo "  show_help"
    echo ""
}

# Mostrar ayuda si se ejecuta el script
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    show_help
else
    echo "Comandos cargados! Ejecuta 'show_help' para ver la lista completa"
fi
