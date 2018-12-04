## Overview  
The "weather" app is a flask web service returning current weather and forecast  
weather data from [https://openweathermap.org/](https://openweathermap.org/).  
Data can be returned in metric or imperial units as well as temperatures in Kelvin.
## Requirements  
 * Python v3.7.1
 * Docker (optional) I used version 18.09.0
## Assumptions  
 * Validity of API responses (XML validity, response following API spec, etc) is taken  
 for granted and is not checked.
 * Maximum forecast in the future can be 5 days in advance  
 * If only day is used with no time data returned will be that of the  
 first time window provided by openwaethermap API  
 * City names must be present in the json file provided by openweathermap  
 [here](http://bulk.openweathermap.org/sample/).  
 * City name must be in the same format as in this json (upper and lower case letters)  
 * Uniqueness cannot be guaranteed just by the city name. In case multiples entries are  
 present the first city encountered will be used.
## Running through terminal  
Install python requirements  
```buildoutcfg
pip install -r requirements.txt
```
APPID provided by openweather.
```buildoutcfg
export APPID=<appid_provided_by_openweather>
```
One could also configure the environment the app is deployed on. there are two enviroment configurations.  
 * DEV (Debug mode turned on)
 * PROD
```buildoutcfg
export ENV=<DEV or PROD>
```
Run the app
```buildoutcfg
python run.py
```

Note: in case of multiple python interpreters are installed, make sure  
the app is run with Python v.3.7
## Running with Docker  
First build the container and tag it appropriately.  
```buildoutcfg
docker build -t <tag_name> .
```

APPID provided by openweather.
```buildoutcfg
export APPID=<appid_provided_by_openweather>
```

One could also configure the environment the app is deployed on. there are two enviroment configurations.  
 * DEV (Debug mode turned on)
 * PROD
```buildoutcfg
export ENV=<DEV or PROD>
```

Run the container
```buildoutcfg
docker run -e APPID=$APPID -e ENV=$ENV -p 8080:8080 <tag_name>
```

## Routes  
### /ping  - /ping/
#### GET
Testing route  
Response:  
```buildoutcfg
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 73
Server: Werkzeug/0.14.1 Python/3.7.1
Date: Tue, 04 Dec 2018 10:33:06 GMT

{
  "name": "weatherservice", 
  "status": "ok", 
  "version": "1.0.0"
}

```
#### /forecast/``<city>`` - /forecast/``<city>``/  
####  GET  
Response: 
```buildoutcfg
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 113
Server: Werkzeug/0.14.1 Python/3.7.1
Date: Tue, 04 Dec 2018 10:38:35 GMT

{
  "clouds": string, 
  "humidity": string, 
  "pressure": string, 
  "temperature": string
}

```

Query parameters:  
In case the "at" parameter is present forecast data is returned otherwise  
the current weather data.
 * at (optional)  
 Date following ISO8601 format  
 * units (optional)  
 Can be one of: 
    * metric  
    * imperial  
    * default

Errors
 * 400 - Invalid date (format, past date or future date beyond the maximum 5 day limit)
 ```buildoutcfg
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 96
Server: Werkzeug/0.14.1 Python/3.7.1
Date: Tue, 04 Dec 2018 11:00:29 GMT

{
  "error": "Invalid date format!", 
  "error_code": "invalid date"
}

```
Or:  
```buildoutcfg
{
  "error": "Date in the past!", 
  "error_code": "invalid date"
}

```
Or:  
```buildoutcfg
{
  "error": "Maximum forecast can be 5 days in the future!", 
  "error_code": "invalid date"
}

```
 * 404 - Invalid city name  
 ```buildoutcfg
HTTP/1.0 404 NOT FOUND
Content-Type: application/json
Content-Length: 81
Server: Werkzeug/0.14.1 Python/3.7.1
Date: Tue, 04 Dec 2018 11:08:12 GMT

{
  "error": "Cannot find city 'city_name'", 
  "error_code": "city_not_found"
}
```
 * 500 - Server Error  
 ```buildoutcfg
HTTP/1.0 500 INTERNAL SERVER ERROR
Content-Type: application/json
Content-Length: 80
Server: Werkzeug/0.14.1 Python/3.7.1
Date: Tue, 04 Dec 2018 10:37:02 GMT

{
  "error": "Something went wrong", 
  "error_code": "internal_server_error"
}

```
## Tests  
A test script is provided testing the routes and their responce codes. 
```buildoutcfg
python route_test.py
python function_test.py
```