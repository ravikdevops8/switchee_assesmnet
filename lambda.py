import json
import boto3
import requests
from datetime import datetime, timedelta

def get_historical_weather_data(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,humidity_2m_max,humidity_2m_min",
        "timezone": "UTC"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def aggregate_data(data):
    aggregated = []
    for daily in data['daily']['time']:
        date = daily
        temp_max = data['daily']['temperature_2m_max'][data['daily']['time'].index(date)]
        temp_min = data['daily']['temperature_2m_min'][data['daily']['time'].index(date)]
        hum_max = data['daily']['humidity_2m_max'][data['daily']['time'].index(date)]
        hum_min = data['daily']['humidity_2m_min'][data['daily']['time'].index(date)]
        
        temp_median = (temp_max + temp_min) / 2
        hum_median = (hum_max + hum_min) / 2
        
        aggregated.append({
            'date': date,
            'temperature_median': temp_median,
            'humidity_median': hum_median
        })
    return aggregated

def save_to_dynamodb(property_id, aggregated_data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WeatherData')
    with table.batch_writer() as batch:
        for data in aggregated_data:
            item = {
                'property_id': property_id,
                'date': data['date'],
                'temperature_median': data['temperature_median'],
                'humidity_median': data['humidity_median']
            }
            batch.put_item(Item=item)

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        property_id = body['property_id']
        lat = body['lat']
        lon = body['lon']
        start_date = body['start_date']
        end_date = body['end_date']
        
        weather_data = get_historical_weather_data(lat, lon, start_date, end_date)
        aggregated_data = aggregate_data(weather_data)
        save_to_dynamodb(property_id, aggregated_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data processed successfully')
    }
