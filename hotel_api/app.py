from flask import Flask
from hotel_api.extensions import api, db, bcrypt


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    app.config.from_pyfile("settings.py", silent=True)

    if settings_override:
        app.config.update(settings_override)

    from hotel_api.resources.users import users_ns
    from hotel_api.resources.auth import auth_ns
    from hotel_api.resources.reservations import reservations_ns
    from hotel_api.resources.hotels import hotels_ns
    from hotel_api.resources.availabilities import availabilities_ns

    # Register namespaces for resources available through the api
    api.add_namespace(users_ns, path="/users")
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(hotels_ns, path="/hotels")
    api.add_namespace(availabilities_ns, path="/availabilities")
    api.add_namespace(reservations_ns, path="/reservations")

    from hotel_api.extensions import api_bp

    app.register_blueprint(api_bp)  # sets up routing for api application

    extensions(app)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    db.init_app(app)
    bcrypt.init_app(app)

    return None