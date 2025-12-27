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
    Servicio 4: Obtener datos de sensores
    HTTP GET - Retorna los datos de detección de sensores
    """
    try:
        # Obtener parámetros de query
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        alert_level = query_params.get('alert_level')  # NORMAL, DANGER
        
        # Si se especifica un nivel de alerta, usar el índice
        if alert_level:
            response = sensor_data_table.query(
                IndexName='AlertLevelIndex',
                KeyConditionExpression=Key('alert_level').eq(alert_level),
                ScanIndexForward=False,  # Orden descendente por timestamp
                Limit=limit
            )
        else:
            # Scan de toda la tabla (limitado)
            response = sensor_data_table.scan(Limit=limit)
        
        items = response.get('Items', [])
        
        # Ordenar por timestamp descendente
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'count': len(items),
                'data': items
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
