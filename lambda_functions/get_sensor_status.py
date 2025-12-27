import json
import boto3 # type: ignore
import os
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key # type: ignore

dynamodb = boto3.resource('dynamodb')
sensor_status_table = dynamodb.Table(os.environ['SENSOR_STATUS_TABLE'])


def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Servicio 8: Obtener estado de sensores y cámaras
    HTTP GET - Retorna el estado actual de los sensores
    """
    try:
        # Obtener parámetros de query
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        only_problems = query_params.get('only_problems', 'false').lower() == 'true'
        
        # Si solo queremos problemas, usar el índice
        if only_problems:
            response = sensor_status_table.query(
                IndexName='StatusAlertIndex',
                KeyConditionExpression=Key('has_alert').eq('true'),
                ScanIndexForward=False,
                Limit=limit
            )
        else:
            response = sensor_status_table.scan(Limit=limit)
        
        items = response.get('Items', [])
        
        # Ordenar por timestamp descendente
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Obtener el estado más reciente
        latest_status = items[0] if items else None
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'count': len(items),
                'latest_status': latest_status,
                'history': items
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
