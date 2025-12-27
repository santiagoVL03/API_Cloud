import json
import boto3 # type: ignore
import os
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key # type: ignore

dynamodb = boto3.resource('dynamodb')
alerts_table = dynamodb.Table(os.environ['ALERTS_TABLE'])
sensor_data_table = dynamodb.Table(os.environ['SENSOR_DATA_TABLE'])


def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Servicio 6: Obtener warnings y danger alerts
    HTTP GET - Retorna alertas y warnings registrados
    """
    try:
        # Obtener parámetros de query
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 100))
        alert_type_filter = query_params.get('alert_type')
        
        # Obtener alertas de la tabla de alertas
        if alert_type_filter:
            alerts_response = alerts_table.query(
                IndexName='AlertTypeIndex',
                KeyConditionExpression=Key('alert_type').eq(alert_type_filter),
                ScanIndexForward=False,
                Limit=limit
            )
        else:
            alerts_response = alerts_table.scan(Limit=limit)
        
        alerts = alerts_response.get('Items', [])
        
        # Obtener registros con nivel de alerta DANGER
        danger_response = sensor_data_table.query(
            IndexName='AlertLevelIndex',
            KeyConditionExpression=Key('alert_level').eq('DANGER'),
            ScanIndexForward=False,
            Limit=limit
        )
        
        danger_records = danger_response.get('Items', [])
        
        # Combinar y formatear datos
        all_alerts = []
        
        # Procesar alertas enviadas
        for alert in alerts:
            all_alerts.append({
                'alert_id': alert.get('alert_id'),
                'timestamp': alert.get('timestamp'),
                'type': 'EMAIL_ALERT',
                'alert_type': alert.get('alert_type'),
                'status': alert.get('status'),
                'sns_message_id': alert.get('sns_message_id')
            })
        
        # Procesar registros de peligro
        for record in danger_records:
            all_alerts.append({
                'alert_id': record.get('id'),
                'timestamp': record.get('timestamp'),
                'type': 'DANGER_DETECTION',
                'alert_level': record.get('alert_level'),
                'alert': record.get('alert'),
                'danger_alert': record.get('danger_alert'),
                'danger_conditions': record.get('danger_conditions', []),
                'temperature': float(record.get('temperature', 0)),
                'humidity': float(record.get('humidity', 0)),
                'probability_smoke': float(record.get('probability_smoke', 0))
            })
        
        # Ordenar por timestamp descendente
        all_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'count': len(all_alerts),
                'alerts': all_alerts
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
