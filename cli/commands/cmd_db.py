from random import randint
import click

from hotel_api.app import create_app
from hotel_api.extensions import db
from hotel_api.models import Hotels, Reservations
from lib.seed_data.seed_data import get_hotels, reservations

app = create_app()
db.app = app

@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass

@click.command()
def init():
    """
    Initialize the database.

    :return: None
    """

    db.drop_all()
    db.create_all()

    return None

@click.command()
def seed():
    """
    Seed the database with inital data.

    :return: 
    """

    # Seed Hotels
    hotels = get_hotels()
    for hotel in hotels:
        new_hotel = Hotels(**hotel)
        new_hotel.add_hotel(total_double_rooms=randint(1,25),
                        total_queen_rooms=randint(1,25),
                        total_king_rooms=randint(1,25))
    
    # Seed Reservations
    for reservation in reservations:
        db.session.add(Reservations(**reservation))
        db.session.commit()
    
    return None

@click.command()
@click.pass_context
def reset(ctx):
    """
    Init and seed automatically.

    :return: None
    """
    ctx.invoke(init)
    ctx.invoke(seed)

    return None


cli.add_command(init)
cli.add_command(seed)
cli.add_command(reset)