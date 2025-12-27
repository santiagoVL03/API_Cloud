import json
import boto3 # type: ignore
import os
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key # type: ignore

dynamodb = boto3.resource('dynamodb')
sensor_data_table = dynamodb.Table(os.environ['SENSOR_DATA_TABLE'])


def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Servicio 5: Obtener datos de detección ML de cámaras
    HTTP GET - Retorna datos de probabilidades de detección
    """
    try:
        # Obtener parámetros de query
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        min_probability = float(query_params.get('min_probability', 0.0))
        
        # Scan de la tabla
        response = sensor_data_table.scan(Limit=limit)
        items = response.get('Items', [])
        
        # Filtrar por probabilidad mínima si se especifica
        if min_probability > 0:
            items = [
                item for item in items 
                if (float(item.get('probability_vapor', 0)) >= min_probability or
                    float(item.get('probability_smug', 0)) >= min_probability or
                    float(item.get('probability_smoke', 0)) >= min_probability or
                    float(item.get('probability_fog', 0)) >= min_probability)
            ]
        
        # Preparar datos de detección ML
        ml_detection_data = []
        for item in items:
            ml_detection_data.append({
                'id': item.get('id'),
                'timestamp': item.get('timestamp'),
                'detection': {
                    'vapor': float(item.get('probability_vapor', 0)),
                    'smug': float(item.get('probability_smug', 0)),
                    'smoke': float(item.get('probability_smoke', 0)),
                    'fog': float(item.get('probability_fog', 0))
                },
                'alert': item.get('alert', ''),
                'danger_alert': item.get('danger_alert', ''),
                'alert_level': item.get('alert_level', 'NORMAL')
            })
        
        # Ordenar por timestamp descendente
        ml_detection_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'count': len(ml_detection_data),
                'data': ml_detection_data
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
