from flask import Flask
from hotel_api.extensions import api, db


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

    from hotel_api.resources.reservations import ReservationList, Reservation
    from hotel_api.resources.hotels.hotels import HotelList, Hotel
    from hotel_api.resources.hotels.availabilities import Availabilities

    # Register the routes for resources available through the api
    base = "/hotel/api/v0.1/"
    api.add_resource(ReservationList, f"{base}reservations", endpoint="reservations")
    api.add_resource(
        Reservation, f"{base}reservations/<int:id>", endpoint="reservation"
    )
    api.add_resource(HotelList, f"{base}hotels", endpoint="hotels")
    api.add_resource(Hotel, f"{base}hotels/<int:id>", endpoint="hotel")
    api.add_resource(Availabilities, f"{base}availabilities", endpoint="availabilities")

    extensions(app)  # must initialize api after adding routes

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