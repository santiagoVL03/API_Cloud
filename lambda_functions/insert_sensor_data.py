import json
import boto3 # type: ignore
import os
from datetime import datetime
from decimal import Decimal
import uuid

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

sensor_data_table = dynamodb.Table(os.environ['SENSOR_DATA_TABLE'])
alerts_table = dynamodb.Table(os.environ['ALERTS_TABLE'])

TEMP_THRESHOLD = float(os.environ['TEMP_THRESHOLD'])
HUMIDITY_THRESHOLD = float(os.environ['HUMIDITY_THRESHOLD'])
SMOKE_THRESHOLD = float(os.environ['SMOKE_THRESHOLD'])
FOG_THRESHOLD = float(os.environ['FOG_THRESHOLD'])
ALERT_FUNCTION = os.environ['ALERT_FUNCTION_NAME']


def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Servicio 1: Inserción de datos de sensores
    Recibe datos del API Fog Computing, los almacena en DynamoDB
    y verifica umbrales para generar alertas
    """
    try:
        # Parsear body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        data = body.get('data', {})
        
        # Validar datos requeridos
        required_fields = ['temperature', 'humidity', 'probability_vapor', 
                          'probability_smug', 'probability_smoke', 'probability_fog']
        
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Generar ID y timestamp
        record_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Convertir a Decimal para DynamoDB
        temperature = Decimal(str(data['temperature']))
        humidity = Decimal(str(data['humidity']))
        prob_vapor = Decimal(str(data['probability_vapor']))
        prob_smug = Decimal(str(data['probability_smug']))
        prob_smoke = Decimal(str(data['probability_smoke']))
        prob_fog = Decimal(str(data['probability_fog']))
        
        # Determinar nivel de alerta
        alert_level = "NORMAL"
        danger_conditions = []
        
        # Verificar umbrales
        if float(temperature) > TEMP_THRESHOLD:
            danger_conditions.append(f"High temperature: {temperature}°C")
            alert_level = "DANGER"
        
        if float(humidity) < HUMIDITY_THRESHOLD:
            danger_conditions.append(f"Low humidity: {float(humidity)*100}%")
            alert_level = "DANGER"
        
        if float(prob_smoke) > SMOKE_THRESHOLD:
            danger_conditions.append(f"High smoke probability: {float(prob_smoke)*100}%")
            alert_level = "DANGER"
        
        # CRÍTICO: Verificar niebla (peligro para conducción)
        if float(prob_fog) > FOG_THRESHOLD:
            danger_conditions.append(f"HIGH FOG DETECTED: {float(prob_fog)*100}% - DRIVING HAZARD!")
            alert_level = "DANGER"
        
        # Preparar item para DynamoDB
        item = {
            'id': record_id,
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity,
            'probability_vapor': prob_vapor,
            'probability_smug': prob_smug,
            'probability_smoke': prob_smoke,
            'probability_fog': prob_fog,
            'alert': data.get('alert', ''),
            'danger_alert': data.get('danger_alert', ''),
            'alert_level': alert_level,
            'danger_conditions': danger_conditions
        }
        
        # Guardar en DynamoDB
        sensor_data_table.put_item(Item=item)
        
        # Si hay condiciones de peligro, llamar al servicio de alertas
        if alert_level == "DANGER" and danger_conditions:
            try:
                alert_payload = {
                    'alert_type': 'DANGER_THRESHOLD_EXCEEDED',
                    'timestamp': timestamp,
                    'conditions': danger_conditions,
                    'sensor_data': {
                        'temperature': float(temperature),
                        'humidity': float(humidity),
                        'probability_smoke': float(prob_smoke),
                        'probability_fog': float(prob_fog),
                        'alert': data.get('alert', ''),
                        'danger_alert': data.get('danger_alert', '')
                    }
                }
                
                # Invocar función de alertas
                lambda_client.invoke(
                    FunctionName=ALERT_FUNCTION,
                    InvocationType='Event',  # Asíncrono
                    Payload=json.dumps(alert_payload)
                )
                
                print(f"Alert triggered for record {record_id}")
            except Exception as e:
                print(f"Error triggering alert: {str(e)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Data inserted successfully',
                'record_id': record_id,
                'timestamp': timestamp,
                'alert_level': alert_level,
                'danger_conditions': danger_conditions
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
