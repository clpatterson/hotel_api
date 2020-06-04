from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, fields, marshal
from resources.reservations import ReservationList, Reservation
from resources.hotels import HotelList, Hotel
from resources.users import UserList, User


app = Flask(__name__)
api = Api(app)

# Register the routes for resources available through the api
api.add_resource(ReservationList, '/hotel/api/v1.0/reservations', 
                 endpoint ='reservations')
api.add_resource(Reservation, '/hotel/api/v1.0/reservations/<int:id>', 
                 endpoint = 'reservation')
api.add_resource(HotelList, '/hotel/api/v1.0/hotels', 
                 endpoint = 'hotels')
api.add_resource(Hotel, '/hotel/api/v1.0/hotels/<int:id>', 
                 endpoint = 'hotel')
api.add_resource(UserList, '/hotel/api/v1.0/users', 
                 endpoint = 'users')
api.add_resource(User, '/hotel/api/v1.0/users/<int:id>', 
                 endpoint = 'user')

if __name__ == '__main__':
    app.run(debug=True)
