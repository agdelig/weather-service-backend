from flask import Blueprint, jsonify, render_template, abort


forecast_blueprint = Blueprint('forecast', __name__)


@forecast_blueprint.route('/')
def forecast():
    with open('./VERSION', 'r') as file:
        version = file.read().strip()
        responce = {
            'name': 'weatherservice',
            'status': 'ok',
            'version': version
        }

        return jsonify(responce)

