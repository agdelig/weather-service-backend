from flask import Blueprint, jsonify, render_template, abort


ping_blueprint = Blueprint('ping', __name__)


@ping_blueprint.route('/')
def ping():
    with open('./VERSION', 'r') as file:
        version = file.readlines()[0].strip()
        responce = {
            'name': 'weatherservice',
            'status': 'ok',
            'version': version
        }

        return jsonify(responce)

