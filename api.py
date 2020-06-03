from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, fields, marshal
from resources.reservations import ReservationList, Reservation

app = Flask(__name__)
api = Api(app)

# Register the routes for resources available through the api
api.add_resource(ReservationList, '/hotel/api/v1.0/reservations', 
                 endpoint ='reservations')
api.add_resource(Reservation, '/hotel/api/v1.0/reservations/<int:id>', 
                 endpoint = 'reservation')

if __name__ == '__main__':
    app.run(debug=True)