#CONEXION A API OPNE-METEO
import requests

from django.conf import settings


def get_coordenates(city_name):
    
    """Obtiene las coordenadas de una ciudad utilizando la API de geocodificación de Open-Meteo.
    Args:        city_name (str): Nombre de la ciudad para la cual se desean obtener las coordenadas.
    Returns:        dict: Diccionario con las coordenadas de la ciudad (latitud y longitud) o None si no se pudo obtener la información.
    """
    
    url = 'https://geocoding-api.open-meteo.com/v1/search'
    params = {
        'name': city_name,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_weather_params(city):
    
    """Obtiene los parámetros de clima (p y f) para una ciudad específica utilizando la API de Open-Meteo.
    Args:
        city (str): Nombre de la ciudad para la cual se desean obtener los parámetros de clima.
        Returns:
        dict: Diccionario con los parámetros de clima (p y f) calculados en función de la temperatura, humedad y velocidad del viento.
    """
    
    url = 'https://api.open-meteo.com/v1/forecast'
    coordenates = get_coordenates(city)
    lat = coordenates['results'][0]['latitude']
    lon = coordenates['results'][0]['longitude']

    response = requests.get(url=url, params={
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m'
    })
    data = response.json()
    
    temperature = data['current']['temperature_2m']
    humidity = data['current']['relative_humidity_2m']
    wind = data['current']['wind_speed_10m']
    
    p_base = 0.05
    f_base = 0.001
    
    if wind > 30:
        p_base *= 0.5
    if humidity > 70:
        p_base *= 1.5
        f_base *= 2.0
    if temperature > 35:
        f_base *= 2.0
        
    
    return {'p':p_base,'f':f_base}

