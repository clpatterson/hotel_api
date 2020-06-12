#from api import db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    reservations = db.relationship('Reservations', backref='users', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def add_user(self):
        db.session.add(self)
        db.session.commit()

class Reservations(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    checkin_date = db.Column(db.DateTime, nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False)
    guest_full_name = db.Column(db.String, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    last_updated_date = db.Column(db.DateTime, nullable=False)
    is_cancelled = db.Column(db.Boolean, nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False)
    room_inventory = db.relationship('RoomInventory', backref='reservations', lazy=True)

    def __repr__(self):
        return f'<Reservation_id {self.id}>'

class Hotels(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    rooms = db.relationship('Rooms', backref='hotels', lazy=True)

    def __repr__(self):
        return f'<Hotel {self.name}>'

    def add_hotel(self):
        db.session.add(self)
        db.session.commit()

class Rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)

    def __repr__(self):
        return f'<Hotel_id {self.hotel_id} Room_id {self.id}>'

class RoomInventory(db.Model):
    __tablename__ = 'room_inventory'
    date = db.Column(db.DateTime, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=True)

    def __repr__(self):
        return f'<Date {self.date} Hotel_id {self.hotel_id} Room_id {self.room_id}>'
