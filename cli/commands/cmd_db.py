import click

from sqlalchemy_utils import database_exists, create_database

from hotel_api.app import create_app
from hotel_api.extensions import db
from hotel_api.models import Hotels, Reservations
from lib.seed_data.seed_data import get_hotels, reservations, seed_db

app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option(
    "--with-testdb/ --no-with-testdb", default=False, help="Create a test db too?"
)
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()
    db.create_all()

    if with_testdb:
        db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        db_uri = f"{db_uri}_test"

        if not database_exists(db_uri):
            create_database(db_uri)
    return None


@click.command()
@click.option("--dev/ --no-dev", default=False, help="Seeding a dev environment?")
def seed(dev):
    """
    Seed the database with inital data.

    :return:
    """
    seed_db(dev)

    return None


@click.command()
@click.option(
    "--with-testdb/ --no-with-testdb", default=False, help="Create a test db too?"
)
@click.option("--dev/ --no-dev", default=False, help="Seeding a dev environment?")
@click.pass_context
def reset(ctx, with_testdb, dev):
    """
    Init and seed automatically.

    :param with_testdb: Create a test database
    :param dev: Seed database with dev data
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed, dev=dev)

    return None


cli.add_command(init)
cli.add_command(seed)
cli.add_command(reset)