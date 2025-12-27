import json
import boto3 # type: ignore
import os
from datetime import datetime, timedelta
from decimal import Decimal
from boto3.dynamodb.conditions import Key # type: ignore

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

sensor_status_table = dynamodb.Table(os.environ['SENSOR_STATUS_TABLE'])
ALERT_FUNCTION = os.environ['ALERT_FUNCTION_NAME']


def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Servicio 7: Verificación periódica del estado de sensores
    Se ejecuta cada 2 horas vía EventBridge
    Verifica el estado de los sensores y envía alertas si hay problemas
    """
    try:
        print("Starting sensor status verification...")
        
        # Obtener el estado más reciente (últimos 30 minutos)
        now = datetime.utcnow()
        time_threshold = (now - timedelta(minutes=30)).isoformat()
        
        # Buscar registros con problemas
        response = sensor_status_table.query(
            IndexName='StatusAlertIndex',
            KeyConditionExpression=Key('has_alert').eq('true'),
            ScanIndexForward=False,
            Limit=10
        )
        
        problem_records = response.get('Items', [])
        
        # Si no hay registros recientes, obtener el más reciente
        if not problem_records:
            all_response = sensor_status_table.scan(Limit=1)
            all_items = all_response.get('Items', [])
            if all_items:
                all_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                latest_record = all_items[0]
                
                # Verificar si el registro más reciente tiene problemas
                if latest_record.get('has_alert') == 'true':
                    problem_records = [latest_record]
        
        # Analizar problemas encontrados
        if problem_records:
            latest_problem = problem_records[0]
            
            failed_sensors = []
            failed_cameras = []
            
            # Verificar sensores
            if not latest_problem.get('status_sensor_humidity', True):
                failed_sensors.append("Sensor de Humedad")
            
            if not latest_problem.get('status_sensor_temperature', True):
                failed_sensors.append("Sensor de Temperatura")
            
            # Verificar cámaras
            cameras = latest_problem.get('status_cameras', [])
            for camera in cameras:
                if not camera.get('status', False):
                    failed_cameras.append(camera.get('camera', 'Unknown'))
            
            # Si hay sensores o cámaras con problemas, enviar alerta
            if failed_sensors or failed_cameras:
                alert_payload = {
                    'alert_type': 'SENSOR_MALFUNCTION',
                    'timestamp': latest_problem.get('timestamp'),
                    'failed_sensors': failed_sensors,
                    'failed_cameras': failed_cameras,
                    'record_id': latest_problem.get('id')
                }
                
                # Invocar función de alertas
                lambda_client.invoke(
                    FunctionName=ALERT_FUNCTION,
                    InvocationType='Event',
                    Payload=json.dumps(alert_payload)
                )
                
                print(f"Alert sent for sensor malfunction: {failed_sensors + failed_cameras}")
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Sensor verification completed - Problems found',
                        'failed_sensors': failed_sensors,
                        'failed_cameras': failed_cameras,
                        'alert_sent': True
                    })
                }
        
        print("Sensor verification completed - All systems operational")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Sensor verification completed - All systems operational',
                'alert_sent': False
            })
        }
        
    except Exception as e:
        print(f"Error in sensor verification: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
