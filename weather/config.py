import os, logging


class Config(object):
    app_id = os.getenv('APPID')
    host = '0.0.0.0'


class DevConfig(Config):
    path = 'weather.config.DevConfig'
    name = 'DEVELOPMENT'
    DEBUG = True
    TESTING = True
    LOGGING_LEVEL = logging.DEBUG


class ProdConfig(Config):
    path ='weather.config.ProdConfig'
    name = 'PRODUCTION'
    DEBUG = False
    TESTING = False
    LOGGING_LEVEL = logging.WARNING


configurations = {
    'DEV': DevConfig,
    'PROD': ProdConfig
}

