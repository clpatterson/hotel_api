from datetime import datetime
from flask import abort, request
from flask_restful import Resource, reqparse, fields, marshal

# TODO: create a postgres database and store these there
reservations = [
    {
    'id': 1,
    'username': 'Charlie',
    'checkin_date': u'2020-05-01',
    'checkout_date': u'2020-05-03',
    'guest_full_name': u'Roger Briggs',
    'hotel_id': 1,
    'room_id': 1,
    'created_date': u'2020-05-01T14:09:13.702495',
    'last_updated_date': u'2020-05-01T14:09:13.702495',
    'is_cancelled': False,
    'is_completed': True
    },
    {
    'id': 2,
    'username': 'Charlie',
    'checkin_date': u'2020-05-03',
    'checkout_date': u'2020-05-04',
    'guest_full_name': u'Miguel Grinberg',
    'hotel_id': 1,
    'room_id': 2,
    'created_date': u'2020-05-01T14:09:13.702495',
    'last_updated_date': u'2020-05-01T14:09:13.702495',
    'is_cancelled': False,
    'is_completed': True
    },
    {
    'id': 3,
    'username': 'Charlie',
    'checkin_date': u'2020-05-03',
    'checkout_date': u'2020-05-04',
    'guest_full_name': u'Oprah Winfrey',
    'hotel_id': 1,
    'room_id': 1,
    'created_date': u'2020-05-01T14:09:13.702495',
    'last_updated_date': u'2020-05-01T14:09:13.702495',
    'is_cancelled': False,
    'is_completed': True
    }
]

# for creating public / more manage-able urls
reservation_fields = {
    'username': fields.String,
    'checkin_date': fields.String,
    'checkout_date': fields.String,
    'guest_full_name': fields.String,
    'hotel_id': fields.Integer,
    'room_id': fields.Integer,
    'created_date': fields.String,
    'last_updated_date': fields.String,
    'is_cancelled': fields.Boolean,
    'is_completed': fields.Boolean,
    'uri': fields.Url('reservation')
}

# Argument parser for both ReservationList and Reservations
reqparse = reqparse.RequestParser() # these lines are for input validation
reqparse.add_argument('username', type = str, required = True,
    help = "No username provided.", location = 'json')
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
        return { 'reservations': [marshal(reservation, reservation_fields) for reservation in reservations] }
    
    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        # TODO: add created_date, last_updated date, is_completed, is_cancelled
        reservation = {
                        'id': reservations[-1]['id'] + 1 if len(reservations) > 0 else 1,
                        'username': args['username'],
                        'checkin_date': args['checkin_date'],
                        'checkout_date': args['checkout_date'],
                        'guest_full_name': args['guest_full_name'],
                        'hotel_id': args['hotel_id'],
                        'room_id': 1, # ToDo: Query inventory and assign
                        'created_date': datetime.now().isoformat(),
                        'last_updated_date': datetime.now().isoformat(),
                        'is_cancelled': False,
                        'is_completed': False

                       }
        reservations.append(reservation)
        return {'reservations': marshal(reservation, reservation_fields)}, 201

class Reservation(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(Reservation, self).__init__()
    
    def get(self, id):
        """List specified reservation."""
        reservation = [res for res in reservations if res['id'] == id]
        if len(reservation) == 0:
            abort(404)
        return { 'reservation': marshal(reservation[0], reservation_fields)} 
    
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