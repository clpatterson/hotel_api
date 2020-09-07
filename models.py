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
    desired_room_type = db.Column(db.String, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_cancelled = db.Column(db.Boolean, nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Reservation_id {self.id}>'

    def add_reservation(self):
        available = RoomInventory.check_available(hotel_id=self.hotel_id,
                                                  room_type=self.desired_room_type,
                                                  checkin_date=self.checkin_date,
                                                  checkout_date=self.checkout_date)
        if available == True:
            RoomInventory.update_inventory(hotel_id=self.hotel_id,
                                           room_type=self.desired_room_type,
                                           checkin_date=self.checkin_date,
                                           checkout_date=self.checkout_date,
                                           flag='reserve')
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_reservation(id):
        reservation = Reservations.query.get_or_404(id)
        reservation_fields = row2dict(reservation)
        return {'fields': reservation_fields, 'objects': reservation}

    @staticmethod
    def get_reservations():
        reservations = Reservations.query.all()
        reservations_fields = [row2dict(res) for res in reservations]
        return {'fields': reservations_fields, 'objects': reservations}

    @staticmethod
    def update(id, args):
        reservation = Reservations.get_reservation(id)
        diff = [k for k in args if args[k] != reservation['fields'][k]]
        print(diff)
        if len(diff) == 0:
            print("done")
            return reservation
        else:
            print("in loop")
            if 'user_id' in diff:
                # TODO: Throw Error: can't change user_id on res (cancel > make new res)
                print('user_id')
                return reservation
            if 'hotel_id' in diff:
                # TODO: Throw Error: can't change hotel_id (cancel > make new res)
                print('hotel_id')
                return reservation
            if 'full_guest_name' in diff:
                print("guest name")
                reservation['objects'].full_guest_name = args['full_guest_name']
                reservation['objects'].last_modified_date = datetime.now()
            if bool(set(['checkin_date', 'checkout_date', 'desired_room_type']).intersection(diff)):
                print("new res details")
                available = RoomInventory.check_available(hotel_id=args['hotel_id'],
                                                            room_type=args['desired_room_type'],
                                                            checkin_date=args['checkin_date'],
                                                            checkout_date=args['checkout_date'])
                if available == True:
                    print("true")
                    RoomInventory.update_inventory(hotel_id=args['hotel_id'],
                                                    room_type=args['desired_room_type'],
                                                    checkin_date=args['checkin_date'],
                                                    checkout_date=args['checkout_date'],
                                                    flag='reserve')
                    reservation['objects'].last_modified_date = datetime.now()
                    db.session.commit()
                else:
                    return # TODO: add error handling to say change not available
        return reservation

    @staticmethod
    def delete(id):
        reservation = Reservations.get_or_404(id)
        reservation.is_cancelled = True
        reservation.last_modified_date = datetime.now()
        db.session.commit()
        RoomInventory.update_inventory(hotel_id=id,
                                       room_type=reservation.desired_room_type,
                                       checkin_date=reservation.checkin_date,
                                       checkout_date=reservation.checkout_date,
                                       flag='free')
        return reservation



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
                        continue  # Throw error: hotels cannot shrink in size
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
                        continue  # Throw error: hotels cannot shrink in size
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
                        continue  # Throw error: hotels cannot shrink in size
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
        """Update the max capacity for given room types when hotel changes."""
        hotel = Hotels.get_hotel(hotel_id)
        hotel = hotel['fields']
        room_types = {'double': hotel['total_double_rooms'],
                      'queen': hotel['total_queen_rooms'],
                      'king': hotel['total_king_rooms']}
        last_modified_date = datetime.now()
        for k, v in room_types.items():
            table = RoomInventory.__table__
            stmt = table.update().\
                         where(and_(table.columns.hotel_id == hotel_id,
                                    table.columns.room_type == k)).\
                         values(max_rooms_available=v, 
                                last_modified_date=last_modified_date)
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
        dates = db.session.query(RoomInventory.date, 
                                 RoomInventory.max_rooms_available - RoomInventory.rooms_reserved).\
                            filter(RoomInventory.hotel_id == hotel_id,
                                   RoomInventory.room_type == room_type,
                                   RoomInventory.date.between(checkin_date, 
                                                         checkin_date)).all()
        available = all([date[1] > 0 for date in dates]) # must have rooms on all dates
        # TODO: if this date range does not work, provide helpful error info
        return available
    
    @staticmethod
    def update_inventory(hotel_id, room_type, checkin_date, checkout_date, flag):
        """Reserve or free room inventory for a single reservation."""
        dates = db.session.query(RoomInventory).\
                            filter(RoomInventory.hotel_id == hotel_id,
                                   RoomInventory.room_type == room_type,
                                   RoomInventory.date.between(checkin_date, 
                                                         checkin_date)).\
                               all()
        for date in dates:
            if flag == 'reserve':
                date.rooms_reserved += 1
            else:
                date.rooms_reserved -= 1
        db.session.commit()
        return
        # TODO: add error handling and rollback if something happens

                    
        
            