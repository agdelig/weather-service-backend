import requests as req, os
from flask import Blueprint, jsonify, request, abort
from weather import cache
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json, iso8601, pytz
from urllib.parse import splitquery, quote_plus,  urlparse, parse_qs

base_api_url = 'http://api.openweathermap.org/data/2.5/'
api_id = os.getenv("APPID")

forecast_blueprint = Blueprint('forecast', __name__)

with open("./weather/resources/city_list.json", "r") as read_file:
    city_codes = json.load(read_file)


@forecast_blueprint.route('/parse')
def parse_time():
    url = request.url
    print(request.url_charset)
    print(splitquery(url))
    base_url = request.base_url
    decode = url
    parsed_url = urlparse(decode)
    q = parse_qs(parsed_url.query.replace('+', '%2B'), encoding='utf-8')
    print(quote_plus(parsed_url.query))
    print(q)

    t = q.get('at')
    print(f'{decode} --------------------- {t}')
    dt = iso8601.parse_date('2018-10-14T14:34:40-0100')
    d = iso8601.parse_date(t[0])

    if dt == d:
        return'true'
    else:
        return 'false'
    #return f'{dt:%B %d, %Y}'


def parse_date(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query.replace('+', '%2B'), encoding='utf-8')
    date_param = query_params.get('at')
    try:
        requested_date = iso8601.parse_date(date_param[0])
    except Exception:
        return 'nope'

    now_utc = pytz.utc.localize(datetime.utcnow())

    if requested_date > now_utc + timedelta(days=5):
        return 'tooooooooooooooooooo much'
    elif requested_date < now_utc:
        return 'are you nuts?'
    else:
        return'OK'



#@forecast_blueprint.route('/<city>')
@forecast_blueprint.route('/<city>/')
def city_weather(city):
    #try:
    cities_list = city_name_to_code(city)
    return jsonify(create_response(cities_list))
    #except Exception:
        #abort(403)


def create_response(c_c):
    units_param = ''
    if request.args.get('units') is not None:
        units_param = f'&units={request.args.get("units")}'

    if request.args.get('at') is not None:
        return specific_date_forecast(c_c, units_param)
    else:
        r = []
        for city in c_c:
            r.append(current_weather(city, units_param))
            return r


def specific_date_forecast(city, units_param):
    url = f'{base_api_url}forecast' \
          f'?id={city[0].get("id")}&appid={api_id}&mode=xml{units_param}'

    xml_content = consume_weather_api(url)


    #try:
    date = parse_date(url=request.url)
    forecast = xml_content.find('forecast')

    r = []
    for child in forecast:
        r.append(create_response_from_xml(child))
    #except Exception:
        #abort(403)
    return r


def current_weather(city, units_param):
    url = f'{base_api_url}weather' \
          f'?id={city.get("id")}&appid={api_id}&mode=xml{units_param}'

    xml_content = consume_weather_api(url)

    return create_response_from_xml(xml_content)


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
        raise Exception

    return city_entry

