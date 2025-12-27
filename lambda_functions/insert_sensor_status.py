import json
import boto3 # type: ignore
import os
from datetime import datetime
from decimal import Decimal
import uuid

dynamodb = boto3.resource('dynamodb')
sensor_status_table = dynamodb.Table(os.environ['SENSOR_STATUS_TABLE'])


def lambda_handler(event, context):
    """
    Servicio 2: Inserción del estado de sensores y cámaras
    Recibe el estado de los sensores y cámaras y lo almacena en DynamoDB
    """
    try:
        # Parsear body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        data = body.get('data', {})
        
        # Validar datos requeridos
        required_fields = ['alert', 'status_sensor_humidity', 
                          'status_sensor_temperature', 'status_cameras']
        
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Generar ID y timestamp
        record_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Determinar si hay algún sensor o cámara con problemas
        has_alert = "true" if data['alert'] else "false"
        
        # Verificar estado de sensores
        sensors_ok = (data['status_sensor_humidity'] and 
                     data['status_sensor_temperature'])
        
        # Verificar estado de cámaras
        cameras_status = data['status_cameras']
        cameras_ok = all(camera.get('status', False) for camera in cameras_status)
        
        # Si algún sensor o cámara tiene problemas, marcar alerta
        if not sensors_ok or not cameras_ok:
            has_alert = "true"
        
        # Preparar item para DynamoDB
        item = {
            'id': record_id,
            'timestamp': timestamp,
            'alert': data['alert'],
            'has_alert': has_alert,
            'status_sensor_humidity': data['status_sensor_humidity'],
            'status_sensor_temperature': data['status_sensor_temperature'],
            'status_cameras': cameras_status,
            'sensors_ok': sensors_ok,
            'cameras_ok': cameras_ok,
            'all_systems_operational': sensors_ok and cameras_ok
        }
        
        # Guardar en DynamoDB
        sensor_status_table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Sensor status inserted successfully',
                'record_id': record_id,
                'timestamp': timestamp,
                'has_alert': has_alert,
                'sensors_ok': sensors_ok,
                'cameras_ok': cameras_ok
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
