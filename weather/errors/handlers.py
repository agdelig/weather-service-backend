from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    message = {
        "error": error.description.get('message'),
        "error_code": "city_not_found"
    }

    return jsonify(message), 404


@errors.app_errorhandler(400)
def error_403(error):
    message = {
        "error": error.description.get('message'),
        "error_code": "invalid date"
    }
    return jsonify(message), 400


@errors.app_errorhandler(500)
def error_500(error):
    message = {
        "error": "Something went wrong",
        "error_code": "internal_server_error"
    }
    return jsonify(message), 500
