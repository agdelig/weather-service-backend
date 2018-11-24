import requests as req, os
from flask import Blueprint, jsonify, request, abort
from weather import cache
import xml.etree.ElementTree as ET


forecast_blueprint = Blueprint('forecast', __name__)


@forecast_blueprint.route('/<city>')
def city_forecast(city):
    d = consume_weather_api(city)

    clouds = d.find('clouds')
    humidity = d.find('humidity')
    pressure = d.find('pressure')
    temperature = d.find('temperature')

    responce = {
        "clouds": f'{clouds.get("name")}',
        "humidity": f'{humidity.get("value")} {humidity.get("unit")}',
        "pressure": f'{pressure.get("value")} {pressure.get("unit")}',
        "temperature": f'{temperature.get("value")} {temperature.get("unit")}',
        "full": 'jh'
    }

    return jsonify(responce)


@forecast_blueprint.route('/<city>/')
def city_forecast_with_params(city):
    a = request.args

    return jsonify(a)


def consume_weather_api(city):
    id = os.getenv("APPID")
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city},uk&appid={id}&mode=xml'
    x = cache.get(url)
    if x is None:
        print('caching...')
        x = req.get(url)
        cache.set(url, x, timeout=600)

    e_tree = ET.fromstring(x.content)

    return e_tree

