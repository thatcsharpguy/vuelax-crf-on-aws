import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

db_env_vars = [
    "DB_DRIVERNAME",
    "DB_USERNAME",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "DB_DATABASE",
]


def get_connection_url():
    arguments = {k[3:].lower(): os.environ[k] for k in db_env_vars}
    return URL(**arguments)


def get_engine():
    return create_engine(get_connection_url(), echo=True)


@contextmanager
def get_session():
    sess = sessionmaker(bind=get_engine())()
    yield sess
    sess.commit()
