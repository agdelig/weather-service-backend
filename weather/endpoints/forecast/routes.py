import requests as req, os
from flask import Blueprint, jsonify, request, abort
from weather import cache
import xml.etree.ElementTree as ET
import json


forecast_blueprint = Blueprint('forecast', __name__)

with open("./weather/resources/city_list.json", "r") as read_file:
    city_codes = json.load(read_file)


@forecast_blueprint.route('/<city>')
@forecast_blueprint.route('/<city>/')
def city_weather(city):
    c_c = city_name_to_code(city)

    return jsonify(current_weather(c_c, request.args))

'''
@forecast_blueprint.route('/<city>/')
def city_forecast_with_params(city):
    a = request.args

    return jsonify(a)
'''


def current_weather(city, params=None):
    print(city)
    id = os.getenv("APPID")
    units_param = ''
    forecast_type = 'weather'

    if params.get('at') is not None:
        forecast_type = 'forecast/daily'

    if params.get('units') is not None:
        units_param = f'&units={params.get("units")}'

    url = f'http://api.openweathermap.org/data/2.5/{forecast_type}' \
          f'?lat={city.get("coord").get("lat")}&lon={city.get("coord").get("lon")}&appid={id}&mode=xml{units_param}'

    print(url)

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


def city_name_to_code(city):
    city_entry = list(filter(lambda c: c['name'] == city, city_codes))

    if len(city_entry) == 0:
        raise Exception
    else:
        return city_entry[0]

