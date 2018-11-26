from flask import Flask
from .config import Config
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .endpoints.ping.routes import ping_blueprint
    from .endpoints.forecast.routes import forecast_blueprint

    app.register_blueprint(ping_blueprint, url_prefix='/ping')
    app.register_blueprint(forecast_blueprint, url_prefix='/forecast')

    return app

