import requests as req, os
from flask import Blueprint, jsonify, request, abort
from weather import cache
import xml.etree.ElementTree as ET


forecast_blueprint = Blueprint('forecast', __name__)


@forecast_blueprint.route('/<city>')
def city_weather(city):

    return jsonify(current_weather(city, request.args))


@forecast_blueprint.route('/<city>/')
def city_forecast_with_params(city):
    a = request.args

    return jsonify(a)


def current_weather(city, params=None):
    id = os.getenv("APPID")
    units_param = ''
    forecast_type = 'weather'

    if params.get('at') is not None:
        forecast_type = 'forecast'

    if params.get('units') is not None:
        units_param = f'&units={params.get("units")}'

    url = f'http://api.openweathermap.org/data/2.5/{forecast_type}' \
          f'?q={city},uk&appid={id}&mode=xml{units_param}'

    xml_content = consume_weather_api(url)

    return create_responce(xml_content)


def consume_weather_api(url):
    request_content = cache.get(url)
    if request_content is None:

        weather_request = req.get(url)
        print('caching...')

        if weather_request.status_code is not 200:
            raise Exception

        request_content = weather_request.content
        cache.set(url, request_content, timeout=600)

    e_tree = ET.fromstring(request_content)

    return e_tree


def create_responce(xml_content):
    clouds = xml_content.find('clouds')
    humidity = xml_content.find('humidity')
    pressure = xml_content.find('pressure')
    temperature = xml_content.find('temperature')

    response = {
        "clouds": f'{clouds.get("name")}',
        "humidity": f'{humidity.get("value")} {humidity.get("unit")}',
        "pressure": f'{pressure.get("value")} {pressure.get("unit")}',
        "temperature": f'{temperature.get("value")} {temperature.get("unit")}'
    }

    return response

