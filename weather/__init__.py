from flask import Flask
import weather.config as con
import os
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


def create_app():
    app = Flask(__name__)
    configuration = con.configurations[os.getenv('ENV', 'DEV')]
    print(f'Running on {configuration.name}')
    app.config.from_object(configuration.path)

    from weather.endpoints.ping.routes import ping_blueprint
    from weather.endpoints.forecast.routes import forecast_blueprint
    from weather.errors.handlers import errors

    app.register_blueprint(ping_blueprint, url_prefix='/ping')
    app.register_blueprint(forecast_blueprint, url_prefix='/forecast')
    app.register_blueprint(errors)

    return app

