from datetime import datetime
from flask import abort, request
from flask_restful import Resource, reqparse, fields, marshal
from models import db, Reservations


# for creating public / more manage-able urls
reservation_fields = {
    'user_id': fields.Integer,
    'checkin_date': fields.String,
    'checkout_date': fields.String,
    'guest_full_name': fields.String,
    'hotel_id': fields.Integer,
    'created_date': fields.String,
    'last_updated_date': fields.String,
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

class ReservationList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(ReservationList, self).__init__()
    
    def get(self):
        """List all reservations."""
        allReservations = Reservations.query.all()
        return { 'reservations': [marshal(reservation, reservation_fields) for reservation in allReservations] }
    
    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        # TODO: add created_date, last_updated date, is_completed, is_cancelled
        reservation = {
                        #'id': reservations[-1]['id'] + 1 if len(reservations) > 0 else 1,
                        'user_id': args['user_id'],
                        'checkin_date': args['checkin_date'],
                        'checkout_date': args['checkout_date'],
                        'guest_full_name': args['guest_full_name'],
                        'hotel_id': args['hotel_id'],
                        'created_date': datetime.now().isoformat(),
                        'last_updated_date': datetime.now().isoformat(),
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
        reservation = Reservations.query.get_or_404(id)
        return { 'reservation': marshal(reservation, reservation_fields)} 
    
    def put(self, id):
        """Update specified reservation."""
        reservation = [res for res in reservations if res['id'] == id]
        if len(reservation) == 0:
            abort(404)
        reservation = reservation[0]
        args = self.reqparse.parse_args()
        for k,v in args.items():
            if v is not None:
                reservation[k] = v
        reservation['last_updated_date'] = datetime.now().isoformat()
        return { 'reservation': marshal(reservation, reservation_fields)}
    
    def delete(self, id):
        """Delete specified reservation."""
        reservation = [res for res in reservations if res['id'] == id]
        if len(reservation) == 0:
            abort(404)
        reservation = reservation[0]
        reservation['is_cancelled'] = True
        reservation['last_updated_date'] = datetime.now().isoformat()
        return {'cancelled': True}