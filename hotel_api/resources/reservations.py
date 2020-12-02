from datetime import datetime, date
from flask import abort, request
from flask_restx import Resource, reqparse, fields, marshal
from hotel_api.models import db, Reservations


# for creating public / more manage-able urls
reservation_fields = {
    "checkin_date": fields.Date,
    "checkout_date": fields.Date,
    "guest_full_name": fields.String,
    "desired_room_type": fields.String,
    "hotel_id": fields.Integer,
    "created_date": fields.DateTime,
    "last_modified_date": fields.DateTime,
    "is_cancelled": fields.Boolean,
    "is_completed": fields.Boolean,
    "uri": fields.Url("reservation"),
}

# Argument parser for both ReservationList and Reservations
reqparse = reqparse.RequestParser()  # these lines are for input validation
reqparse.add_argument(
    "checkin_date",
    type=lambda s: date.fromisoformat(s),
    required=True,
    help="No checkin date provided.",
    location="json",
)
reqparse.add_argument(
    "checkout_date",
    type=lambda s: date.fromisoformat(s),
    required=True,
    help="No checkout date provided.",
    location="json",
)
reqparse.add_argument(
    "hotel_id", type=int, required=True, help="No hotel id provided.", location="json"
)
reqparse.add_argument(
    "guest_full_name",
    type=str,
    required=True,
    help="No guest name provided.",
    location="json",
)
reqparse.add_argument(
    "desired_room_type",
    type=str,
    required=True,
    help="No guest name provided.",
    location="json",
)


class ReservationList(Resource):
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse
        super(ReservationList, self).__init__(*args, **kwargs)

    def get(self):
        """List all reservations."""
        reservations = Reservations.query.all()
        return {
            "reservations": [marshal(res, reservation_fields) for res in reservations]
        }

    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        reservation = {
            "checkin_date": args["checkin_date"],
            "checkout_date": args["checkout_date"],
            "guest_full_name": args["guest_full_name"],
            "desired_room_type": args["desired_room_type"],
            "hotel_id": args["hotel_id"],
            "created_date": datetime.now(),
            "last_modified_date": datetime.now(),
            "is_cancelled": False,
            "is_completed": False,
        }
        reservation = Reservations(**reservation)
        reservation.add()
        return {"reservations": marshal(reservation, reservation_fields)}, 201


class Reservation(Resource):
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse
        super(Reservation, self).__init__(*args, **kwargs)

    def get(self, id):
        """List specified reservation."""
        reservation = Reservations.query.get_or_404(id)
        return {"reservation": marshal(reservation, reservation_fields)}

    def put(self, id):
        """Update specified reservation."""
        args = self.reqparse.parse_args()
        reservation = Reservations.query.get_or_404(id)
        reservation.update(args)
        return {"reservation": marshal(reservation, reservation_fields)}

    def delete(self, id):
        """Delete specified reservation."""
        reservation = Reservations.query.get_or_404(id)
        reservation.delete()
        return {"cancelled": True}
