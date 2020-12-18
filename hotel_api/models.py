from datetime import datetime, date, timedelta

import jwt
from flask import current_app, abort
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_

from lib.util_datetime import daterange, months_out
from lib.util_sqlalchemy import row2dict
from hotel_api.extensions import db, bcrypt


class BaseTable(object):
    __table_args__ = {"schema": "hotel_api"}
    created_date = db.Column(db.DateTime, nullable=False)
    last_modified_date = db.Column(db.DateTime, nullable=False)


class BlacklistedTokens(BaseTable, db.Model):
    __tablename__ = "blacklisted_tokens"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, expires_at):
        self.created_date = datetime.now()
        self.last_modified_date = datetime.now()
        self.token = token
        self.expires_at = datetime.fromtimestamp(expires_at)

    def __repr__(self):
        return f"<BlacklistToken token={self.token}>"

    def add(self):
        db.session.add(self)
        db.session.commit()

        return None

    @classmethod
    def check_blacklist(cls, token):
        exists = cls.query.filter_by(token=token).first()
        return True if exists else False


class Users(BaseTable, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_deactivated = db.Column(db.Boolean, default=False, nullable=False)
    reservations = db.relationship("Reservations", backref="reservations", lazy=True)

    def __init__(self, user_name="", email="", password=""):
        self.user_name = user_name.lower()
        self.email = email.lower()
        self.password = bcrypt.generate_password_hash(password).decode()

    def __repr__(self):
        return f"<User_id {self.id}, admin={self.is_admin}>"

    def add(self, admin=False):
        """
        Add new user.
        """
        # TODO: How should users who wish to reactivate their profile be handled? Reactivate method?
        # TODO: Validate user names. Should they have special chars, etc?
        email = Users.query.filter(Users.email == self.email).first()
        if email:
            abort(400, "User with this email already exists.")

        user_name = Users.query.filter(Users.user_name == self.user_name).first()
        if user_name:
            abort(400, "User with user_name already exists.")

        if admin:
            self.is_admin = True

        self.created_date = datetime.now()
        self.last_modified_date = datetime.now()
        db.session.add(self)
        db.session.commit()

        return None

    def delete(self):
        """
        Deactivate user and cancel all user's outstanding reservations.
        """
        self.is_deactivated = True

        for reservation in self.reservations:
            if not reservation.is_cancelled:
                reservation.delete()

        self.last_modified_date = datetime.now()
        db.session.commit()

        return None

    def update(self, args):
        if args["user_name"]:
            self.user_name = args["user_name"]
        if args["email"]:
            self.email = args["email"]

        self.last_modified_date = datetime.now()
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "email_key" in e.orig.args[0]:
                abort(400, "User with this email already exists. Update failed.")
            if "user_name_key" in e.orig.args[0]:
                abort(400, "User with this user_name already exists. Update failed.")

        return None

    def check_password(self, password):
        """
        Check provided user password against stored user password.
        """
        return bcrypt.check_password_hash(self.password, password)

    def encode_access_token(self):
        """Return JWT token with expiration, id, and role for user."""
        now = datetime.now()
        token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
        token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
        expire = now + timedelta(hours=token_age_h, minutes=token_age_m)

        if current_app.config["TESTING"]:
            expire = now + timedelta(seconds=5)

        payload = dict(exp=expire, iat=now, sub=self.id, admin=self.is_admin)
        key = current_app.config.get("SECRET_KEY")

        return jwt.encode(payload, key, algorithm="HS256")

    @staticmethod
    def decode_access_token(access_token):
        if isinstance(access_token, bytes):
            access_token = access_token.decode("ascii")

        if access_token.startswith("Bearer "):
            split = access_token.split("Bearer")
            access_token = split[1].strip()

        try:
            key = current_app.config.get("SECRET_KEY")
            payload = jwt.decode(access_token, key, algorithms="HS256")

        except jwt.exceptions.ExpiredSignatureError:
            return dict(
                status="Failed", message="Access token expired. Please log in again."
            )

        except jwt.exceptions.InvalidTokenError:
            return dict(status="Failed", message="Invalid token. Please log in.")

        if BlacklistedTokens.check_blacklist(access_token):
            return dict(
                status="Failed", message="Token blacklisted. Please log in again."
            )

        user_dict = dict(
            status="Success",
            id=payload["sub"],
            admin=payload["admin"],
            token=access_token,
            expires_at=payload["exp"],
        )

        return user_dict


class Reservations(BaseTable, db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    guest_full_name = db.Column(db.String, nullable=False)
    customer_user_id = db.Column(
        db.Integer, db.ForeignKey("hotel_api.users.id"), nullable=False
    )
    desired_room_type = db.Column(db.String, nullable=False)
    hotel_id = db.Column(
        db.Integer, db.ForeignKey("hotel_api.hotels.id"), nullable=False
    )
    is_cancelled = db.Column(db.Boolean, nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Reservation_id {self.id}>"

    def serialize(self):
        """
        Serialize sqlalchemy row object into dictionary.
        """
        return row2dict(self)

    def add(self):
        available = RoomInventory.check_available(
            hotel_id=self.hotel_id,
            room_type=self.desired_room_type,
            checkin_date=self.checkin_date,
            checkout_date=self.checkout_date,
        )
        if available == True:
            RoomInventory.update_inventory(
                hotel_id=self.hotel_id,
                room_type=self.desired_room_type,
                checkin_date=self.checkin_date,
                checkout_date=self.checkout_date,
                flag="reserve",
            )
            db.session.add(self)
            db.session.commit()
        else:
            abort(
                400,
                "This reservation is invalid or unavailable.\
                Ensure hotel is available for dates and room type.",
            )

        return None

    def update(self, args):
        diff = [k for k in args if args[k] != self.__dict__[k]]
        print(diff)
        if len(diff) == 0:
            print("done")
            return None
        else:
            print("in loop")
            if "hotel_id" in diff:
                abort(
                    400,
                    "Cannot alter hotel on reservation.\
                     Cancel and make a new reservation.",
                )
            if "customer_user_id" in diff:
                abort(
                    400,
                    "Cannot alter customer on reservation.\
                     Cancel and make a new reservation.",
                )
            if "full_guest_name" in diff:
                print("guest name")
                self.full_guest_name = args["full_guest_name"]
            if bool(
                set(
                    ["checkin_date", "checkout_date", "desired_room_type"]
                ).intersection(diff)
            ):
                print("new res details")
                available = RoomInventory.check_available(
                    hotel_id=args["hotel_id"],
                    room_type=args["desired_room_type"],
                    checkin_date=args["checkin_date"],
                    checkout_date=args["checkout_date"],
                )
                if available == True:
                    print("true")
                    # Reserve inventory for changed reservation
                    RoomInventory.update_inventory(
                        hotel_id=args["hotel_id"],
                        room_type=args["desired_room_type"],
                        checkin_date=args["checkin_date"],
                        checkout_date=args["checkout_date"],
                        flag="reserve",
                    )
                    # Release inventory for old reservation
                    RoomInventory.update_inventory(
                        hotel_id=self.hotel_id,
                        room_type=self.desired_room_type,
                        checkin_date=self.checkin_date,
                        checkout_date=self.checkout_date,
                        flag="release",
                    )
                    # Update reservation to reflect changes
                    self.checkin_date = args["checkin_date"]
                    self.checkout_date = args["checkout_date"]
                    self.desired_room_type = args["desired_room_type"]
                else:
                    db.session.rollback()
                    abort(
                        400,
                        "Reservation change failed.\
                        Altered reservation is unavailable.",
                    )

        self.last_modified_date = datetime.now()
        db.session.commit()

        return None

    def delete(self):
        if self.is_cancelled == True:  # Reservation has already been cancelled.
            return None

        self.is_cancelled = True
        self.last_modified_date = datetime.now()

        db.session.commit()

        RoomInventory.update_inventory(
            hotel_id=self.hotel_id,
            room_type=self.desired_room_type,
            checkin_date=self.checkin_date,
            checkout_date=self.checkout_date,
            flag="release",
        )

        return None


class Hotels(BaseTable, db.Model):
    __tablename__ = "hotels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    established_date = db.Column(db.String, nullable=False)
    proprietor = db.Column(db.String, nullable=True)
    astrd_diameter = db.Column(db.Float, nullable=False)
    astrd_surface_composition = db.Column(db.String, nullable=True)
    ephem_data = db.Column(db.String, nullable=False)
    rooms = db.relationship(
        "Rooms", backref="hotels", lazy=True, cascade="all, delete-orphan"
    )
    room_inventory = db.relationship(
        "RoomInventory",
        backref="room_inventory",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Hotel {self.name}>"

    def serialize(self):
        """
        Serialize sqlalchemy row object into dictionary.
        """
        return row2dict(self)

    def add_hotel(
        self, total_double_rooms, total_queen_rooms, total_king_rooms, inv_months=12
    ):
        """Add a new hotel and its rooms to the database."""
        db.session.add(self)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            abort(400, "Hotel already exists.")
        # add all rooms to rooms table
        rooms = Rooms.create_rooms(
            hotel_id=self.id,
            double_rooms=total_double_rooms,
            queen_rooms=total_queen_rooms,
            king_rooms=total_king_rooms,
        )
        db.session.add_all(rooms)
        db.session.commit()
        RoomInventory.bulk_add_inventory(
            hotel_id=self.id,
            max_double_capactiy=total_double_rooms,
            max_queen_capactiy=total_queen_rooms,
            max_king_capacity=total_king_rooms,
            start_date=date.today(),
            end_date=months_out(date.today(), inv_months),
        )

    def get_room_counts(self):
        """Return counts of double, queen, and king rooms."""
        rooms = (
            db.session.query(func.count(Rooms.type), Rooms.type)
            .group_by(Rooms.type)
            .order_by(Rooms.type)
            .filter(Rooms.hotel_id == self.id)
            .all()
        )
        if rooms == []:  # Newly created hotels will not have rooms
            return {
                "total_double_rooms": 0,
                "total_queen_rooms": 0,
                "total_king_rooms": 0,
            }
        else:
            return {
                "total_double_rooms": rooms[0][0],
                "total_queen_rooms": rooms[2][0],
                "total_king_rooms": rooms[1][0],
            }

    @staticmethod
    def update_hotel(id, args):
        """Update a hotel's data in the database."""
        hotel = Hotels.get_hotel(id)
        diff = [k for k in args if args[k] != hotel["fields"][k]]
        if len(diff) == 0:
            return hotel
        else:
            for k in diff:  # Specific action for each key
                if k == "name":
                    hotel["objects"].name = args["name"]
                # TODO: refactoring needed below
                elif k == "total_double_rooms":
                    room_diff = (
                        args["total_double_rooms"]
                        - hotel["fields"]["total_double_rooms"]
                    )
                    if room_diff < 0:
                        db.session.rollback()
                        abort(
                            400, "Hotel room counts cannot shrink. They can only grow."
                        )
                    else:
                        new_rooms = [
                            Rooms(
                                hotel_id=id,
                                created_date=datetime.now(),
                                last_modified_date=datetime.now(),
                                type="double",
                            )
                            for n in range(room_diff)
                        ]
                        db.session.add_all(new_rooms)
                elif k == "total_queen_rooms":
                    room_diff = (
                        args["total_queen_rooms"] - hotel["fields"]["total_queen_rooms"]
                    )
                    if room_diff < 0:
                        db.session.rollback()
                        abort(
                            400, "Hotel room counts cannot shrink. They can only grow."
                        )
                    else:
                        new_rooms = [
                            Rooms(
                                hotel_id=id,
                                created_date=datetime.now(),
                                last_modified_date=datetime.now(),
                                type="queen",
                            )
                            for n in range(room_diff)
                        ]
                        db.session.add_all(new_rooms)
                elif k == "total_king_rooms":
                    room_diff = (
                        args["total_king_rooms"] - hotel["fields"]["total_king_rooms"]
                    )
                    if room_diff < 0:
                        db.session.rollback()
                        abort(
                            400, "Hotel room counts cannot shrink. They can only grow."
                        )
                    else:
                        new_rooms = [
                            Rooms(
                                hotel_id=id,
                                created_date=datetime.now(),
                                last_modified_date=datetime.now(),
                                type="king",
                            )
                            for n in range(room_diff)
                        ]
                        db.session.add_all(new_rooms)
            hotel["objects"].last_modified_date = datetime.now()
            db.session.commit()
            RoomInventory.bulk_update_inventory(hotel_id=id)
            hotel = Hotels.get_hotel(id)
            return hotel

    @staticmethod
    def delete_hotel(id):
        """Delete a hotel from the database."""
        hotel = Hotels.query.get_or_404(id)
        db.session.delete(hotel)
        db.session.commit()
        # RoomInventory.bulk_delete_inventory(hotel_id=hotel.id)

    @staticmethod
    def get_hotels():
        """Return a list of hotels with room counts from the database."""
        hotels = Hotels.query.all()
        hotel_list = []
        for hotel in hotels:
            rooms = hotel.get_room_counts()
            hotel = row2dict(hotel)
            hotel = {**hotel, **rooms}  # merge dictionaries
            hotel_list.append(hotel)
        return {"fields": hotel_list, "objects": hotels}

    @staticmethod
    def get_hotel(id):
        """Return a single hotel with room counts from the database."""
        hotel = Hotels.query.get_or_404(id)
        rooms = hotel.get_room_counts()
        hotel_fields = row2dict(hotel)
        hotel_fields = {**hotel_fields, **rooms}  # merge dictionaries
        return {"fields": hotel_fields, "objects": hotel}

    def serialize(self):
        """
        Serialize sqlalchemy row object into dictionary.
        """
        return row2dict(self)


class Rooms(BaseTable, db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    hotel_id = db.Column(
        db.Integer, db.ForeignKey("hotel_api.hotels.id"), nullable=False
    )

    def __repr__(self):
        return f"<Hotel_id {self.hotel_id} Room_id {self.id}>"

    def serialize(self):
        """
        Serialize sqlalchemy row object into dictionary.
        """
        return row2dict(self)

    @staticmethod
    def create_rooms(hotel_id, double_rooms, queen_rooms, king_rooms):
        """Return an array of rooms instances."""
        args = {
            "hotel_id": hotel_id,
            "created_date": datetime.now(),
            "last_modified_date": datetime.now(),
        }
        rooms = []
        for room in range(double_rooms):
            room = Rooms(type="double", **args)
            rooms.append(room)
        for room in range(queen_rooms):
            room = Rooms(type="queen", **args)
            rooms.append(room)
        for room in range(king_rooms):
            room = Rooms(type="king", **args)
            rooms.append(room)
        return rooms


class RoomInventory(BaseTable, db.Model):
    __tablename__ = "room_inventory"
    id = db.Column(db.Integer, primary_key=True)
    # TODO: These are no longer primary keys
    date = db.Column(db.DateTime, nullable=False)
    hotel_id = db.Column(
        db.Integer, db.ForeignKey("hotel_api.hotels.id"), nullable=False
    )
    room_type = db.Column(db.String, nullable=False)
    max_rooms_available = db.Column(db.Integer, nullable=False)
    rooms_reserved = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Date {self.date} Hotel_id {self.hotel_id} Room_type {self.room_type}>"

    def serialize(self):
        """
        Serialize sqlalchemy row object into dictionary.
        """
        return row2dict(self)

    @staticmethod
    def bulk_add_inventory(
        hotel_id,
        max_double_capactiy,
        max_queen_capactiy,
        max_king_capacity,
        start_date,
        end_date,
    ):
        """Add hotel room inventory in bulk for n number of months."""
        room_types = {
            "double": max_double_capactiy,
            "queen": max_queen_capactiy,
            "king": max_king_capacity,
        }
        created_date = datetime.now()
        last_modified_date = datetime.now()
        room_inventory = []
        for date in daterange(start_date, end_date):
            for k, v in room_types.items():
                room_type = dict(
                    created_date=created_date,
                    last_modified_date=last_modified_date,
                    date=date,
                    hotel_id=hotel_id,
                    room_type=k,
                    max_rooms_available=v,
                    rooms_reserved=0,
                )
                room_inventory.append(room_type)
        db.engine.execute(RoomInventory.__table__.insert().values(room_inventory))

    @staticmethod
    def bulk_update_inventory(hotel_id):
        """Update the max capacity for given room types when hotel changes."""
        hotel = Hotels.get_hotel(hotel_id)
        hotel = hotel["fields"]
        room_types = {
            "double": hotel["total_double_rooms"],
            "queen": hotel["total_queen_rooms"],
            "king": hotel["total_king_rooms"],
        }
        last_modified_date = datetime.now()
        for k, v in room_types.items():
            table = RoomInventory.__table__
            stmt = (
                table.update()
                .where(
                    and_(
                        table.columns.hotel_id == hotel_id, table.columns.room_type == k
                    )
                )
                .values(max_rooms_available=v, last_modified_date=last_modified_date)
            )
            db.engine.execute(stmt)

    @staticmethod
    def bulk_delete_inventory(hotel_id):
        """Delete all inventory for a given hotel."""
        table = RoomInventory.__table__
        stmt = table.delete().where(table.columns.hotel_id == hotel_id)
        db.engine.execute(stmt)

    # TODO: update_inventory (when a reservation is made / altered / cancelled)

    @staticmethod
    def check_available(hotel_id, room_type, checkin_date, checkout_date):
        """Check that inventory is available for given data range and room type."""
        last_night = checkout_date - timedelta(days=1)

        dates = (
            db.session.query(
                RoomInventory.date,
                RoomInventory.max_rooms_available - RoomInventory.rooms_reserved,
            )
            .filter(
                RoomInventory.hotel_id == hotel_id,
                RoomInventory.room_type == room_type,
                RoomInventory.date.between(
                    checkin_date.isoformat(), last_night.isoformat()
                ),
            )
            .all()
        )

        if dates:
            available = all(
                [date[1] > 0 for date in dates]
            )  # must have rooms on all dates
            # TODO: if this date range does not work, provide helpful error info
            return available
        else:
            return None

    @staticmethod
    def update_inventory(hotel_id, room_type, checkin_date, checkout_date, flag):
        """Reserve or free room inventory for a single reservation."""
        last_night = checkout_date - timedelta(days=1)

        dates = (
            db.session.query(RoomInventory)
            .filter(
                RoomInventory.hotel_id == hotel_id,
                RoomInventory.room_type == room_type,
                RoomInventory.date.between(
                    checkin_date.isoformat(), last_night.isoformat()
                ),
            )
            .all()
        )
        for _date in dates:
            if flag == "reserve":
                _date.rooms_reserved += 1
            else:  # release inventory
                _date.rooms_reserved -= 1
        db.session.commit()

        return None
