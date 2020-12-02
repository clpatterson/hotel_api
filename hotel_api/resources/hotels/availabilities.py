from datetime import datetime, date, timedelta
from sqlalchemy import text
from flask_restx import Resource, reqparse, fields, marshal
from hotel_api.models import db, Hotels, RoomInventory


hotel_fields = {
    "name": fields.String,
    "established_date": fields.String,
    "proprietor": fields.String,
    "astrd_diameter": fields.Float,
    "astrd_surface_composition": fields.String,
    "uri": fields.Url("hotel"),
}

# Parse search parameters from url query string
reqparse = reqparse.RequestParser()
reqparse.add_argument(
    "name", type=str, required=False, location="args", action="append"
)
reqparse.add_argument("checkin", type=str, required=True, location="args")
reqparse.add_argument("checkout", type=str, required=True, location="args")
reqparse.add_argument(
    "surface_type",
    type=str,
    required=False,
    location="args",
    choices=["silicaceous", "carbonaceous", "enstatite", "metallic", "primitive"],
    action="append",
)
reqparse.add_argument(
    "room_type",
    type=str,
    required=False,
    location="args",
    choices=["king", "queen", "double"],
    action="append",
)


class Availabilities(Resource):
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse
        super(Availabilities, self).__init__(*args, **kwargs)

    def get(self, *args):
        """Return list of hotels matching search criteria."""
        args = self.reqparse.parse_args()
        hotel_filters = []
        room_types = ("double", "queen", "king")
        checkin = args["checkin"]

        # Can't use checkout date in inventory table query so convert to
        #  last night of stay
        checkout_date = datetime.strptime(args["checkout"], "%Y-%m-%d").date()
        checkin_date = datetime.strptime(args["checkin"], "%Y-%m-%d").date()
        lastnight_date = checkout_date - timedelta(days=1)
        lastnight = lastnight_date.strftime("%Y-%m-%d")

        # Get the length of stay in days
        delta = checkout_date - checkin_date
        day_count = delta.days

        if len(args) > 2:
            if args["name"]:
                hotel_filters.append(Hotels.name.in_(args["name"]))
            if args["surface_type"]:
                hotel_filters.append(
                    Hotels.astrd_surface_composition.in_(args["surface_type"])
                )
            if args["room_type"]:
                room_types = tuple(args["room_type"])

        # Search inventory table for hotels with available rooms for stay
        stmt = (
            "with hotel_dates as ( "
            "select distinct hotel_id, date "
            "from room_inventory "
            f"where date between :checkin and :lastnight "
            "and (max_rooms_available - rooms_reserved) > 0 "
            f"and room_type in :room_types "
            "), "
            "hotel_day_count as ( "
            "select distinct hotel_id, count(date) over(PARTITION BY hotel_id) as day_count "
            "from hotel_dates "
            "), "
            "available_hotels as ( "
            "select hotel_id "
            "from hotel_day_count "
            f"where day_count = :day_count "
            ") "
            "select distinct hotel_id "
            "from available_hotels left join hotels on available_hotels.hotel_id = hotels.id; "
        )
        stmt = text(stmt)
        avail_hotels = db.engine.execute(
            stmt,
            checkin=checkin,
            lastnight=lastnight,
            room_types=room_types,
            day_count=day_count,
        ).fetchall()
        avail_hotels = [v[0] for v in avail_hotels]

        # Get hotels with availabilities
        hotel_filters.append(Hotels.id.in_(avail_hotels))
        hotels = db.session.query(Hotels).filter(*hotel_filters).all()
        hotels = [hotel.serialize() for hotel in hotels]

        return {"hotels": [marshal(hotel, hotel_fields) for hotel in hotels]}