import json
import boto3 # type: ignore
import os
from datetime import datetime
from decimal import Decimal
import uuid

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

alerts_table = dynamodb.Table(os.environ['ALERTS_TABLE'])
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']


def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Servicio 3: Envío de alertas por email
    Puede ser invocado por otros servicios o directamente vía HTTP GET
    """
    try:
        # Determinar origen de la invocación
        if 'httpMethod' in event:
            # Invocación desde API Gateway
            if isinstance(event.get('body'), str) and event['body']:
                payload = json.loads(event['body'])
            else:
                payload = event.get('body', {})
        else:
            # Invocación directa desde otra Lambda
            if isinstance(event, str):
                payload = json.loads(event)
            else:
                payload = event
        
        # Extraer información de la alerta
        alert_type = payload.get('alert_type', 'GENERAL_ALERT')
        timestamp = payload.get('timestamp', datetime.utcnow().isoformat())
        
        # Generar ID de alerta
        alert_id = str(uuid.uuid4())
        
        # Construir mensaje de email basado en el tipo de alerta
        subject = ""
        message_body = ""
        
        if alert_type == "DANGER_THRESHOLD_EXCEEDED":
            subject = "🚨 ALERTA CRÍTICA - Umbrales de Peligro Superados"
            conditions = payload.get('conditions', [])
            sensor_data = payload.get('sensor_data', {})
            
            message_body = f"""
╔════════════════════════════════════════════════════════════╗
║   SISTEMA DE DETECCIÓN DE NIEBLA/VAPOR/HUMO - ALERTA     ║
╚════════════════════════════════════════════════════════════╝

⚠️  ALERTA CRÍTICA DETECTADA
Fecha y Hora: {timestamp}
ID de Alerta: {alert_id}

🔴 CONDICIONES PELIGROSAS DETECTADAS:
{chr(10).join(f"  • {condition}" for condition in conditions)}

📊 DATOS DE SENSORES:
  • Temperatura: {sensor_data.get('temperature', 'N/A')}°C
  • Humedad: {sensor_data.get('humidity', 'N/A') * 100 if sensor_data.get('humidity') else 'N/A'}%
  • Probabilidad de Humo: {sensor_data.get('probability_smoke', 'N/A') * 100 if sensor_data.get('probability_smoke') else 'N/A'}%
  • Probabilidad de Niebla: {sensor_data.get('probability_fog', 'N/A') * 100 if sensor_data.get('probability_fog') else 'N/A'}% ⚠️ PELIGRO VIAL

📢 ALERTAS DEL SISTEMA:
  {sensor_data.get('alert', 'Sin alertas adicionales')}

⚡ ACCIÓN REQUERIDA:
  Se recomienda verificar inmediatamente el área monitoreada
  y tomar las medidas de seguridad correspondientes.

═══════════════════════════════════════════════════════════
Sistema Automático de Monitoreo Urbano
            """
            
        elif alert_type == "SENSOR_MALFUNCTION":
            subject = "⚠️ ALERTA - Mal Funcionamiento de Sensores"
            failed_sensors = payload.get('failed_sensors', [])
            failed_cameras = payload.get('failed_cameras', [])
            
            message_body = f"""
╔════════════════════════════════════════════════════════════╗
║   SISTEMA DE DETECCIÓN - FALLO DE SENSORES               ║
╚════════════════════════════════════════════════════════════╝

⚠️  ALERTA DE MANTENIMIENTO
Fecha y Hora: {timestamp}
ID de Alerta: {alert_id}

🔧 SENSORES CON PROBLEMAS:
{chr(10).join(f"  • {sensor}" for sensor in failed_sensors) if failed_sensors else "  ✓ Todos los sensores operativos"}

📹 CÁMARAS CON PROBLEMAS:
{chr(10).join(f"  • Cámara: {camera}" for camera in failed_cameras) if failed_cameras else "  ✓ Todas las cámaras operativas"}

⚡ ACCIÓN REQUERIDA:
  Se requiere revisión técnica del equipamiento reportado
  para restaurar la funcionalidad completa del sistema.

═══════════════════════════════════════════════════════════
Sistema Automático de Monitoreo Urbano
            """
            
        else:
            # Alerta genérica
            subject = "📢 Notificación del Sistema de Detección"
            message_body = f"""
Alerta del Sistema
==================
Tipo: {alert_type}
Fecha y Hora: {timestamp}
ID: {alert_id}

Detalles:
{json.dumps(payload, indent=2, default=decimal_default)}

═══════════════════════════════════════════════════════════
Sistema Automático de Monitoreo Urbano
            """
        
        # Enviar email vía SNS
        sns_response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message_body
        )
        
        # Registrar la alerta enviada en DynamoDB
        alert_record = {
            'alert_id': alert_id,
            'timestamp': timestamp,
            'alert_type': alert_type,
            'sns_message_id': sns_response['MessageId'],
            'payload': json.dumps(payload, default=decimal_default),
            'status': 'sent'
        }
        
        alerts_table.put_item(Item=alert_record)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Alert sent successfully',
                'alert_id': alert_id,
                'sns_message_id': sns_response['MessageId'],
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error sending alert: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
