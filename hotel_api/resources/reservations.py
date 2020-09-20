from datetime import datetime
from flask import abort, request
from flask_restful import Resource, reqparse, fields, marshal
from hotel_api.models import db, Reservations


# for creating public / more manage-able urls
reservation_fields = {
    'user_id': fields.Integer,
    'checkin_date': fields.String,
    'checkout_date': fields.String,
    'guest_full_name': fields.String,
    'desired_room_type': fields.String,
    'hotel_id': fields.Integer,
    'created_date': fields.String,
    'last_modified_date': fields.String,
    'is_cancelled': fields.Boolean,
    'is_completed': fields.Boolean,
    'uri': fields.Url('reservation')
}

# Argument parser for both ReservationList and Reservations
reqparse = reqparse.RequestParser() # these lines are for input validation
reqparse.add_argument('user_id', type = int, required = True,
    help = "No user id provided.", location = 'json')
reqparse.add_argument('checkin_date', type = str, required = True,
    help = "No checkin date provided.", location = 'json')
reqparse.add_argument('checkout_date', type = str, required = True,
    help = "No checkout date provided.", location = 'json')
reqparse.add_argument('hotel_id', type = int, required = True,
    help = "No hotel id provided.", location = 'json')
reqparse.add_argument('guest_full_name', type = str, required = True,
    help = "No guest name provided.", location = 'json')
reqparse.add_argument('desired_room_type', type = str, required = True,
    help = "No guest name provided.", location = 'json')

class ReservationList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(ReservationList, self).__init__()
    
    def get(self):
        """List all reservations."""
        reservations = Reservations.get_reservations()
        return { 'reservations': [marshal(res, reservation_fields) for res in reservations['fields']] }
    
    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        reservation = {
                        'user_id': args['user_id'],
                        'checkin_date': args['checkin_date'],
                        'checkout_date': args['checkout_date'],
                        'guest_full_name': args['guest_full_name'],
                        'desired_room_type': args['desired_room_type'],                        
                        'hotel_id': args['hotel_id'],
                        'created_date': datetime.now(),
                        'last_modified_date': datetime.now(),
                        'is_cancelled': False,
                        'is_completed': False
                       }
        reservation = Reservations(**reservation)
        reservation.add_reservation()
        return {'reservations': marshal(reservation, reservation_fields)}, 201

class Reservation(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(Reservation, self).__init__()
    
    def get(self, id):
        """List specified reservation."""
        reservation = Reservations.get_reservation(id)
        return { 'reservation': marshal(reservation['fields'], reservation_fields)} 
    
    def put(self, id):
        """Update specified reservation."""
        args = self.reqparse.parse_args()
        reservation = Reservations.update(id, args)
        return { 'reservation': marshal(reservation['fields'], reservation_fields)}
    
    def delete(self, id):
        """Delete specified reservation."""
        Reservations.delete(id)
        return {'cancelled': True}