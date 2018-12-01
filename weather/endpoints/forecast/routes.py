import requests as req, os
from flask import Blueprint, jsonify, request, abort
from weather import cache
from weather.endpoints.common import custom_exceptions
import xml.etree.ElementTree as XMLElements
from datetime import datetime, timedelta
import json,iso8601, pytz
from urllib.parse import splitquery, quote_plus,  urlparse, parse_qs
from tzwhere import tzwhere

base_api_url = 'http://api.openweathermap.org/data/2.5/'
api_id = os.getenv("APPID")

forecast_blueprint = Blueprint('forecast', __name__)

with open("./weather/resources/city_list.json", "r") as read_file:
    city_codes = json.load(read_file)


def parse_date(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query.replace('+', '%2B'), encoding='utf-8')
    date_param = query_params.get('at')
    try:
        requested_date = iso8601.parse_date(date_param[0])
    except Exception:
        raise custom_exceptions.DateException

    now_utc = pytz.utc.localize(datetime.utcnow())

    if requested_date > now_utc + timedelta(days=5):
        raise custom_exceptions.DateException#return 'tooooooooooooooooooo much'
    elif requested_date < now_utc:
        raise custom_exceptions.DateException#return 'are you nuts?'
    else:
        return requested_date


@forecast_blueprint.route('/<city>')
@forecast_blueprint.route('/<city>/')
def city_weather(city):
    try:
        cities_list = city_name_to_code(city)
        return jsonify(create_response(cities_list))
    except custom_exceptions.InvalidCityException:
        abort(404)
    except custom_exceptions.DateException:
        abort(400)
    except custom_exceptions.ServerException:
        abort(500)


def create_response(c_c):
    units_param = ''
    if request.args.get('units') is not None:
        units_param = f'&units={request.args.get("units")}'

    if request.args.get('at') is not None:
        return specific_date_forecast(c_c[0], units_param)
    else:
        return current_weather(c_c[0], units_param)


def find_timezone(lat, lon):
    tz_str = tzwhere.tzwhere().tzNameAt(float(lat), float(lon))

    return tz_str


def specific_date_forecast(city, units_param):
    url = f'{base_api_url}forecast' \
          f'?id={city.get("id")}&appid={api_id}&mode=xml{units_param}'

    xml_content = consume_weather_api(url)


    #try:
    date = parse_date(url=request.url)
    forecast = xml_content.find('forecast')
    location_element = xml_content.find('location').find('location')

    tz_name = find_timezone(location_element.get('latitude'), location_element.get('longitude'))
    city_tz = pytz.timezone(tz_name)

    for child in forecast:
        min_timeframe = iso8601.parse_date(child.get('from'), city_tz)
        max_timeframe = iso8601.parse_date(child.get('to'), city_tz)

        if min_timeframe <= date < max_timeframe:
            return create_response_from_xml(child)
    #except Exception:
        #abort(403)


def current_weather(city, units_param):
    url = f'{base_api_url}weather' \
          f'?id={city.get("id")}&appid={api_id}&mode=xml{units_param}'

    xml_content = consume_weather_api(url)

    return create_response_from_xml(xml_content)


def consume_weather_api(url):
    request_content = cache.get(url)
    if request_content is None:

        try:
            weather_request = req.get(url)
        except Exception:
            raise custom_exceptions.ServerException

        if weather_request.status_code is not 200:
            raise custom_exceptions.ServerException

        request_content = weather_request.content
        cache.set(url, request_content, timeout=600)

    e_tree = XMLElements.fromstring(request_content)

    return e_tree


def create_response_from_xml(xml_content):
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
        raise custom_exceptions.InvalidCityException

    return city_entry

