from sqlalchemy import (
    create_engine,
    Engine,
    event,
)
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)

from api.config import settings


def initiate_database():
    """
    The DB for test/prod/dev/local
    :return:
    """
    if settings.driver_name == 'sqlite':
        _db_url = 'sqlite:///unittests'
    else:
        _db_url = (f'{settings.driver_name}{settings.username}:{settings.password}'
                   f'@{settings.host}:{settings.port}/{settings.database}')
    _engine = create_database_engine(_db_url=_db_url, _database_type=settings.database_type)
    return _db_url, _engine


def create_database_engine(_db_url, _database_type):
    """
    Create an engine for the database. For unittests is used sqlite db.
    :param _db_url:
    :param _database_type:
    :return:
    """
    _engine = create_engine(_db_url, pool_pre_ping=True)
    if settings.driver_name == 'sqlite':
        @event.listens_for(Engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
    return _engine


def initialize_database():
    """
    Initialize the database. For unittests is used sqlite db.
    :return:
    """
    Base.metadata.create_all(engine)


db_url, engine = initiate_database()

Session = sessionmaker(bind=engine)
Base = declarative_base()
