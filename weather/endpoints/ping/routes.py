from flask import Blueprint, jsonify, abort
from weather import logger


ping_blueprint = Blueprint('ping', __name__)


@ping_blueprint.route('/')
@ping_blueprint.route('')
def ping():
    try:
        with open('./VERSION', 'r') as file:
            version = file.readlines()[0].strip()
            response = {
                'name': 'weatherservice',
                'status': 'ok',
                'version': version
            }

        return jsonify(response)
    except FileNotFoundError:
        logger.critical('File VERSION not found')
        abort(500)



