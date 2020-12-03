from datetime import datetime, date
from flask import abort, request
from flask_restx import Namespace, Resource, reqparse, fields, marshal
from hotel_api.models import db, Reservations

reservations_ns = Namespace("reservations")

# for creating public / more manage-able urls
reservation_fields = reservations_ns.model(
    "reservations",
    {
        "checkin_date": fields.Date(example="2020-09-02"),
        "checkout_date": fields.Date(example="2020-09-07"),
        "guest_full_name": fields.String(example="Miguel Grinberg"),
        "desired_room_type": fields.String(example="queen"),
        "hotel_id": fields.Integer(example="2"),
        "created_date": fields.DateTime(example="2020-08-01T01:59:39.180982"),
        "last_modified_date": fields.DateTime(example="2020-08-01T01:59:39.180988"),
        "is_cancelled": fields.Boolean(example="false"),
        "is_completed": fields.Boolean(example="true"),
        "uri": fields.Url("reservation", example="/reservations/2"),
    },
)

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

    @reservations_ns.marshal_with(reservation_fields)
    def get(self):
        """List all reservations."""
        reservations = Reservations.query.all()
        return reservations

    @reservations_ns.expect(reqparse)
    @reservations_ns.response(201, "Created")
    @reservations_ns.marshal_with(reservation_fields)
    def post(self):
        """Add a new reservation."""
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
        return reservation, 201


class Reservation(Resource):
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse
        super(Reservation, self).__init__(*args, **kwargs)

    @reservations_ns.marshal_with(reservation_fields)
    def get(self, id):
        """List specified reservation."""
        reservation = Reservations.query.get_or_404(id)
        return reservation

    @reservations_ns.expect(reqparse)
    @reservations_ns.marshal_with(reservation_fields)
    def put(self, id):
        """Update specified reservation."""
        args = self.reqparse.parse_args()
        reservation = Reservations.query.get_or_404(id)
        reservation.update(args)
        return reservation

    @reservations_ns.response(200, '{"cancelled": True}')
    def delete(self, id):
        """Delete specified reservation."""
        reservation = Reservations.query.get_or_404(id)
        reservation.delete()
        return {"cancelled": True}


reservations_ns.add_resource(ReservationList, "", endpoint="reservations")
reservations_ns.add_resource(Reservation, "/<int:id>", endpoint="reservation")
