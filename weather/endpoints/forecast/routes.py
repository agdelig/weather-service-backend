import requests as req, os
from flask import Blueprint, jsonify, request, abort
from weather import cache, logger
from weather.endpoints.common import custom_exceptions
import xml.etree.ElementTree as XMLElements
from datetime import datetime, timedelta
import json,iso8601, pytz
from urllib.parse import urlparse, parse_qs
from tzwhere import tzwhere

base_api_url = 'http://api.openweathermap.org/data/2.5/'
api_id = os.getenv("APPID")

forecast_blueprint = Blueprint('forecast', __name__)

# Read file with city codes provided by openweathermap
try:
    with open("./weather/resources/city_list.json", "r") as read_file:
        city_codes = json.load(read_file)
except FileNotFoundError:
    logger.critical('File "./weather/resources/city_list.json" not found!')
    city_codes = None


def parse_date(url):
    """
    Parses datetime timezone object based on queru param from url.
    Throws DateException if
        1. query string does not follow ISO8601 format
        2. date in the past
        3. date in the future beyond 5 day limit

    :param url:
    :return: datetime object
    """
    logger.info(f'Parsing "{url}"...')
    parsed_url = urlparse(url)
    # Change '+' sign to '%2B' unicode encoded
    query_params = parse_qs(parsed_url.query.replace('+', '%2B'), encoding='utf-8')

    # Get 'at' query parameter
    date_param = query_params.get('at')
    logger.debug(f'Date "{date_param}')

    # Parse 'at' parameter to datetime based on ISO8601 format. Raise DateException if unsuccesful.
    try:
        requested_date = iso8601.parse_date(date_param[0])
        logger.info(f'Date parsed "{requested_date}"')
    except Exception:
        logger.error('Unparsable date!')
        raise custom_exceptions.DateException('Invalid date format!')

    # Create curent time datetime object
    now_utc = pytz.utc.localize(datetime.utcnow())

    # Chech if requested time is valid. Raise DateException if not.
    if requested_date > now_utc + timedelta(days=5):
        logger.error(f'Requested date "{requested_date}" exceeding 5 day limit!')
        raise custom_exceptions.DateException('Maximum forecast can be 5 days in the future!')
    elif requested_date < now_utc:
        logger.error(f'Date "{requested_date}" is in the past!')
        raise custom_exceptions.DateException('Date in the past!')
    else:
        logger.debug(f'Date "{requested_date}" is valid.')
        return requested_date


@forecast_blueprint.route('/<city>/')
@forecast_blueprint.route('/<city>')
def city_weather(city):
    """
    Handles request
    returns
        1. HTTP 200 OK
        2. HTTP 400 Invalid requested time
        3. HTTP 404 Invalid city name
        4. HTTP 500 Server Error

    :param city:
    :return: json Object
    """
    try:
        logger.info(f'Forecast request for "{city}"')
        cities_list = city_name_to_code(city)

        logger.info(f'Response for "{city}".')
        # if more than one city have the same name the first one will be used.
        return jsonify(create_response(cities_list[0]))
    except custom_exceptions.InvalidCityException as err:
        logger.error(err.args[0])
        abort(404, {'message': err.args[0]})
    except custom_exceptions.DateException as err:
        logger.error(err.args[0])
        abort(400, {'message': err.args[0]})
    except custom_exceptions.ServerException as err:
        logger.error(err.args[0])
        abort(500)


def create_response(city):
    """
    Returns dictionary with weather data.

    :param city:
    :return: dict
    """
    units_param = ''
    # Check whether unit param exists.
    logger.debug('Checking for "units" param.')
    if request.args.get('units') is not None:
        units_param = f'&units={request.args.get("units")}'
        logger.debug(f'Units = {units_param}')

    # Check whether curent weather or forecast for specific day has been requested.
    logger.debug('Checking for "at" param.')
    if request.args.get('at') is not None:
        logger.debug(f'Param at = {request.args.get("at")}.')
        return specific_date_forecast(city, units_param)
    else:
        logger.debug('No "at" param.')
        return current_weather(city, units_param)


def find_timezone(lat, lon):
    """
    Find timezone based on lat and lon.

    :param lat:
    :param lon:
    :return: timezone_string
    """
    tz_str = tzwhere.tzwhere().tzNameAt(float(lat), float(lon))
    logger.debug(f'lat: "{lat}" | lon: "{lon}" | timezone: "{tz_str}"')

    return tz_str


def specific_date_forecast(city, units_param):
    """
    Calls openweathermap API to retreive forecast data.

    :param city:
    :param units_param:
    :return: dict
    """

    # Create API url.
    url = f'{base_api_url}forecast' \
          f'?id={city.get("id")}&appid={api_id}&mode=xml{units_param}'

    # Get xml from API
    xml_content = consume_weather_api(url)

    # Get datetime object of forecast datetime requested.
    date = parse_date(url=request.url)

    forecast = xml_content.find('forecast')
    location_element = xml_content.find('location').find('location')

    # Find timezone based on city's lat lon.
    tz_name = find_timezone(location_element.get('latitude'), location_element.get('longitude'))
    city_tz = pytz.timezone(tz_name)

    # Iterate through forecast elements to find the one the requeted forecast time was requeted.
    for child in forecast:
        min_timeframe = iso8601.parse_date(child.get('from'), city_tz)
        max_timeframe = iso8601.parse_date(child.get('to'), city_tz)

        # Return data once time  falls in element's time window
        if min_timeframe <= date < max_timeframe:
            logger.debug(f'Requsted time {date} found in time window {min_timeframe} - {max_timeframe}')
            return create_response_from_xml(child)


def current_weather(city, units_param):
    """
    Retreives current weather data.

    :param city:
    :param units_param:
    :return: dict
    """

    # Create API url.
    url = f'{base_api_url}weather' \
          f'?id={city.get("id")}&appid={api_id}&mode=xml{units_param}'

    # Get API xml response.
    xml_content = consume_weather_api(url)

    return create_response_from_xml(xml_content)


def consume_weather_api(url):
    """
    Access to API to retrieve XML response.
    Throws ServerException if API call is unsuccesfull or
    returns with a non 200 HTTP response

    :param url:
    :return: xml string
    """

    # Check if responce has been cached.
    request_content = cache.get(url)

    # If response has not been cashed make a request to the API.
    if request_content is None:

        try:
            logger.debug(f'Request "{url}".')
            weather_request = req.get(url)
        except Exception:
            raise custom_exceptions.ServerException(f'Error while requesting "{url}"')

        if weather_request.status_code is not 200:
            raise custom_exceptions.ServerException(f'Requst to "{url}" returned with {weather_request.status_code}!')

        request_content = weather_request.content

        # Cache content for 10 min
        logger.debug(f'Caching "{url}"!')
        cache.set(url, request_content, timeout=600)

    e_tree = XMLElements.fromstring(request_content)

    return e_tree


def create_response_from_xml(xml_content):
    """
    Create weather data dictionary based on API xml

    :param xml_content:
    :return: dict
    """
    logger.debug('Parsing XML.')
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
    """
    Search for city name in city_codes
    Throws InvalidCityException if city name does not exist in city_codes.

    :param city:
    :return: list
    """
    if city_codes is None:
        raise custom_exceptions.ServerException('city_codes is None!')

    logger.debug(f'Searching city id for "{city}".')
    city_entry = list(filter(lambda c: c['name'] == city, city_codes))

    if len(city_entry) == 0:
        raise custom_exceptions.InvalidCityException(f"Cannot find city '{city}'")

    return city_entry

