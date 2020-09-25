from flask import Flask
from hotel_api.extensions import api, db


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    from hotel_api.resources.reservations import ReservationList, Reservation
    from hotel_api.resources.hotels import HotelList, Hotel
    from hotel_api.resources.users import UserList, User

    # Register the routes for resources available through the api
    api.add_resource(ReservationList, '/hotel/api/v1.0/reservations',
                     endpoint='reservations')
    api.add_resource(Reservation, '/hotel/api/v1.0/reservations/<int:id>',
                     endpoint='reservation')
    api.add_resource(HotelList, '/hotel/api/v1.0/hotels',
                     endpoint='hotels')
    api.add_resource(Hotel, '/hotel/api/v1.0/hotels/<int:id>',
                     endpoint='hotel')
    api.add_resource(UserList, '/hotel/api/v1.0/users',
                     endpoint='users')
    api.add_resource(User, '/hotel/api/v1.0/users/<int:id>',
                     endpoint='user')
    
    extensions(app) # must initialize api after adding routes

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