from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class BaseTable(object):
    created_date = db.Column(db.DateTime, nullable=False)
    last_modified_date = db.Column(db.DateTime, nullable=False)


class Users(BaseTable, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    reservations = db.relationship('Reservations', backref='users', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def add_user(self):
        db.session.add(self)
        db.session.commit()


class Reservations(BaseTable, db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    checkin_date = db.Column(db.DateTime, nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False)
    guest_full_name = db.Column(db.String, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_cancelled = db.Column(db.Boolean, nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False)
    room_inventory = db.relationship(
        'RoomInventory', backref='reservations', lazy=True)

    def __repr__(self):
        return f'<Reservation_id {self.id}>'

    def add_reservation(self):
        db.session.add(self)
        db.session.commit()


class Hotels(BaseTable, db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    rooms = db.relationship('Rooms', backref='hotels',
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Hotel {self.name}>'

    def add_hotel(self):
        """Add a new hotel to the database."""
        db.session.add(self)
        db.session.commit()

    def get_room_counts(self):
        """Return counts of double, queen, and king rooms."""
        rooms = db.session.query(func.count(Rooms.type), Rooms.type).\
            group_by(Rooms.type).\
            filter(Rooms.hotel_id == self.id).all()
        if rooms == []:  # This will be deleted after bad records are deleted
            return {
                'total_double_rooms': 0,
                'total_queen_rooms': 0,
                'total_king_rooms': 0
            }
        else:
            return {
                'total_double_rooms': rooms[0][0],
                'total_queen_rooms': rooms[1][0],
                'total_king_rooms': rooms[2][0]
            }

    @staticmethod
    def update_hotel(id, data):
        """Update a hotel's data in the database."""
        hotel = Hotels.get_hotel(id)
        hotel['name'] = data['name']
        return hotel

    @staticmethod
    def delete_hotel(id):
        """Delete a hotel from the database."""
        hotel = Hotels.query.get_or_404(id)
        db.session.delete(hotel)
        db.session.commit()

    @staticmethod
    def get_hotels():
        """Return a list of hotels with room counts from the database."""
        hotels = Hotels.query.all()
        hotel_list = []
        for hotel in hotels:
            rooms = hotel.get_room_counts()
            if rooms == None:  # This will be removed after bad db records removed
                continue
            hotel = hotel.__dict__  # convert row object to dict
            hotel = {**hotel, **rooms}  # merge dictionaries
            # TODO: change database schema to include
            hotel['last_updated_date'] = datetime.now()
            hotel_list.append(hotel)
        return hotel_list

    @staticmethod
    def get_hotel(id):
        """Return a single hotel with room counts from the database."""
        hotel = Hotels.query.get_or_404(id)
        rooms = hotel.get_room_counts()
        hotel = {**hotel.__dict__, **rooms}  # merge dictionaries
        # TODO: change database schema to include
        hotel['last_updated_date'] = datetime.now()
        return hotel


class Rooms(BaseTable, db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotels.id'), nullable=False)

    def __repr__(self):
        return f'<Hotel_id {self.hotel_id} Room_id {self.id}>'


class RoomInventory(BaseTable, db.Model):
    __tablename__ = 'room_inventory'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotels.id'), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey(
        'rooms.id'), primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey(
        'reservations.id'), nullable=True)

    def __repr__(self):
        return f'<Date {self.date} Hotel_id {self.hotel_id} Room_id {self.room_id}>'
