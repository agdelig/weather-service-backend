from flask import Flask
import weather.config as con
import os
import logging
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    configuration = con.configurations[os.getenv('ENV', 'DEV')]

    logger.setLevel(configuration.LOGGING_LEVEL)

    # Create the Handler for logging data to a file
    logger_handler = logging.FileHandler('weather.log')
    logger_handler.setLevel(configuration.LOGGING_LEVEL)

    # Create a Formatter for formatting the log messages
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    # Add the Formatter to the Handler
    logger_handler.setFormatter(logger_formatter)

    # Add the Handler to the Logger
    logger.addHandler(logger_handler)
    logger.info('Completed configuring logger()!')

    logger.info(f'Running on {configuration.name}')
    app.config.from_object(configuration.path)

    from weather.endpoints.ping.routes import ping_blueprint
    from weather.endpoints.forecast.routes import forecast_blueprint
    from weather.errors.handlers import errors

    app.register_blueprint(ping_blueprint, url_prefix='/ping')
    app.register_blueprint(forecast_blueprint, url_prefix='/forecast')
    app.register_blueprint(errors)

    return app

