from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql import and_
from common.utils import daterange, months_out, row2dict
from config import config

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
    room_inventory = db.relationship('RoomInventory', backref='room_inventory',
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Hotel {self.name}>'

    def add_hotel(self, total_double_rooms, total_queen_rooms, total_king_rooms):
        """Add a new hotel and its rooms to the database."""
        db.session.add(self)
        db.session.flush()
        # add all rooms to rooms table
        rooms = Rooms.create_rooms(hotel_id=self.id,
                                   double_rooms=total_double_rooms,
                                   queen_rooms=total_queen_rooms,
                                   king_rooms=total_king_rooms)
        db.session.add_all(rooms)
        db.session.commit()
        # TODO: if there is some error above, the bulk add funtion should not run
        RoomInventory.bulk_add_inventory(hotel_id=self.id,
                                         max_double_capactiy=total_double_rooms,
                                         max_queen_capactiy=total_queen_rooms,
                                         max_king_capacity=total_king_rooms,
                                         start_date=date.today(),
                                         end_date=months_out(date.today(), 6))

    def get_room_counts(self):
        """Return counts of double, queen, and king rooms."""
        rooms = db.session.query(func.count(Rooms.type), Rooms.type).\
            group_by(Rooms.type).\
            order_by(Rooms.type).\
            filter(Rooms.hotel_id == self.id).all()
        if rooms == []:  # Newly created hotels will not have rooms
            return {
                'total_double_rooms': 0,
                'total_queen_rooms': 0,
                'total_king_rooms': 0
            }
        else:
            return {
                'total_double_rooms': rooms[0][0],
                'total_queen_rooms': rooms[2][0],
                'total_king_rooms': rooms[1][0]
            }

    @staticmethod
    def update_hotel(id, args):
        """Update a hotel's data in the database."""
        hotel = Hotels.get_hotel(id)
        diff = [k for k in args if args[k] != hotel['fields'][k]]
        if len(diff) == 0:
            return hotel
        else:
            for k in diff:  # Specific action for each key
                if k == 'name':
                    hotel['objects'].name = args['name']
                # TODO: refactoring needed below
                elif k == 'total_double_rooms':
                    room_diff = args['total_double_rooms'] - \
                        hotel['fields']['total_double_rooms']
                    if room_diff < 0:
                        continue  # Issue error: hotels cannot shrink in size
                    else:
                        new_rooms = [Rooms(hotel_id=id,
                                           created_date=datetime.now(),
                                           last_modified_date=datetime.now(),
                                           type='double')
                                     for n in range(room_diff)]
                        db.session.add_all(new_rooms)
                elif k == 'total_queen_rooms':
                    room_diff = args['total_queen_rooms'] - \
                        hotel['fields']['total_queen_rooms']
                    if room_diff < 0:
                        continue  # Issue error: hotels cannot shrink in size
                    else:
                        new_rooms = [Rooms(hotel_id=id,
                                           created_date=datetime.now(),
                                           last_modified_date=datetime.now(),
                                           type='queen')
                                     for n in range(room_diff)]
                        db.session.add_all(new_rooms)
                elif k == 'total_king_rooms':
                    room_diff = args['total_king_rooms'] - \
                        hotel['fields']['total_king_rooms']
                    if room_diff < 0:
                        continue  # Issue error: hotels cannot shrink in size
                    else:
                        new_rooms = [Rooms(hotel_id=id,
                                           created_date=datetime.now(),
                                           last_modified_date=datetime.now(),
                                           type='king')
                                     for n in range(room_diff)]
                        db.session.add_all(new_rooms)
            hotel['objects'].last_modified_date = datetime.now()
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
        return {'fields': hotel_list, 'objects': hotels}

    @staticmethod
    def get_hotel(id):
        """Return a single hotel with room counts from the database."""
        hotel = Hotels.query.get_or_404(id)
        rooms = hotel.get_room_counts()
        hotel_fields = row2dict(hotel)
        hotel_fields = {**hotel_fields, **rooms}  # merge dictionaries
        return {'fields': hotel_fields, 'objects': hotel}


class Rooms(BaseTable, db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotels.id'), nullable=False)

    def __repr__(self):
        return f'<Hotel_id {self.hotel_id} Room_id {self.id}>'

    @staticmethod
    def create_rooms(hotel_id, double_rooms, queen_rooms, king_rooms):
        """Return an array of rooms instances."""
        args = {
            'hotel_id': hotel_id,
            'created_date': datetime.now(),
            'last_modified_date': datetime.now(),
        }
        rooms = []
        for room in range(double_rooms):
            room = Rooms(type='double', **args)
            rooms.append(room)
        for room in range(queen_rooms):
            room = Rooms(type='queen', **args)
            rooms.append(room)
        for room in range(king_rooms):
            room = Rooms(type='king', **args)
            rooms.append(room)
        return rooms


class RoomInventory(BaseTable, db.Model):
    __tablename__ = 'room_inventory'
    id = db.Column(db.Integer, primary_key=True)
    # TODO: These are no longer primary keys
    date = db.Column(db.DateTime, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotels.id'), nullable=False)
    room_type = db.Column(db.String, nullable=False)
    max_rooms_available = db.Column(db.Integer, nullable=False)
    rooms_reserved = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Date {self.date} Hotel_id {self.hotel_id} Room_type {self.room_type}>'

    @staticmethod
    def bulk_add_inventory(hotel_id,
                           max_double_capactiy,
                           max_queen_capactiy,
                           max_king_capacity,
                           start_date,
                           end_date):
        """Add hotel room inventory in bulk for n number of months."""
        room_types = {
            'double': max_double_capactiy,
            'queen': max_queen_capactiy,
            'king': max_king_capacity
        }
        created_date = datetime.now()
        last_modified_date = datetime.now()
        room_inventory = []
        for date in daterange(start_date, end_date):
            for k, v in room_types.items():
                room_type = dict(created_date=created_date,
                                 last_modified_date=last_modified_date,
                                 date=date,
                                 hotel_id=hotel_id,
                                 room_type=k,
                                 max_rooms_available=v,
                                 rooms_reserved=0)
                room_inventory.append(room_type)
        db.engine.execute(
            RoomInventory.__table__.insert().values(room_inventory))

    @staticmethod
    def bulk_update_inventory(hotel_id):
        """Update the max capacity for given rooms types when it changes."""
        hotel = Hotels.get_hotel(hotel_id)
        hotel = hotel['fields']
        room_types = {'double': hotel['total_double_rooms'],
                      'queen': hotel['total_queen_rooms'],
                      'king': hotel['total_king_rooms']}
        last_modified_date = datetime.now()
        for k, v in room_types.items():
            table = RoomInventory.__table__
            db.engine.execute(table.update().\
                              where(and_(table.columns.hotel_id==hotel_id, 
                                         table.columns.room_type==k)).\
                              values(max_rooms_available=v, last_modified_date=last_modified_date))

    @staticmethod
    def bulk_delete_inventory(hotel_id):
        """Delete all inventory for a given hotel."""
        table = RoomInventory.__table__
        db.engine.execute(table.delete().where(table.columns.hotel_id==hotel_id))

    # TODO: update_inventory (when a reservation is made / altered / cancelled)
