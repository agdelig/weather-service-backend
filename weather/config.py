import os


class Config(object):
    app_id = os.getenv('APPID')
    host = '0.0.0.0'


class DevConfig(Config):
    path = 'weather.config.DevConfig'
    name = 'DEVELOPMENT'
    DEBUG = True
    TESTING = True


class ProdConfig(Config):
    path ='weather.config.ProdConfig'
    name = 'PRODUCTION'
    DEBUG = False
    TESTING = False


configurations = {
    'DEV': DevConfig,
    'PROD': ProdConfig
}

