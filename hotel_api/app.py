from flask import Flask

from config.settings import config
from hotel_api.extensions import api, db


def create_app(config_name="development"):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    from hotel_api.resources.reservations import reservations_ns
    from hotel_api.resources.hotels import hotels_ns
    from hotel_api.resources.availabilities import availabilities_ns

    # Register namespaces for resources available through the api
    api.add_namespace(hotels_ns, path="/hotels")
    api.add_namespace(availabilities_ns, path="/availabilities")
    api.add_namespace(reservations_ns, path="/reservations")

    extensions(app)  # must initialize api after adding namespaces

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    api.init_app(app)
    db.init_app(app)

    return None