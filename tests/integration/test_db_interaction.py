import os
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from database.models.base import Base
from main import Service


@pytest.fixture
def environ(docker_ip, docker_services):
    return {
        "JAVA_HOME": os.getenv("JAVA_HOME"),
        "QUEUE_NAME": "",
        "DB_DRIVERNAME": "mysql+pymysql",
        "DB_USERNAME": "VuelaX",
        "DB_PASSWORD": "Password1!",
        "DB_HOST": docker_ip,
        "DB_PORT": "3306",
        "DB_DATABASE": "VuelaX",
    }


@pytest.fixture
def get_test_engine(docker_ip):
    connection_params = {
        "drivername": "mysql+pymysql",
        "username": "VuelaX",
        "password": "Password1!",
        "port": "3306",
        "database": "VuelaX",
    }

    def _get_test_engine():
        return create_engine(URL(**connection_params, host=docker_ip))

    return _get_test_engine


@pytest.fixture
def start_db(docker_ip, docker_services, get_test_engine):
    def is_responsive():

        while True:
            try:
                get_test_engine().connect()
                return True
            except OperationalError:
                return False

    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=is_responsive)

    engine = get_test_engine()

    Base.metadata.create_all(engine)


def test_execution(start_db, get_test_engine):
    expected = [
        (
            1,
            "CDMX",
            "a",
            "Santiago 🇨🇱 + Patagonia",
            "10,309",
            "¡CDMX a Santiago 🇨🇱 + Patagonia 🐧 $10,309!",
        ),
        (
            2,
            "CDMX",
            "a",
            "Ginebra , Suiza",
            "13,832",
            "¡CDMX a Ginebra, Suiza $13,832!",
        ),
        (
            3,
            "CDMX",
            "a",
            "San José , Costa Rica",
            "4,382",
            "¡CDMX a San José, Costa Rica $4,382! 🐸 (Por $1,987 agrega 4 noches de hotel con desayunos)",
        ),
        (
            4,
            "GDL",
            "a",
            "Lima , Perú",
            "3,685",
            "¡GDL a Lima, Perú $3,685! 🇵🇪 (Por $2,004 agrega 4 noches de hotel c/ desayunos)",
        ),
    ]

    offers = [
        "¡CDMX a Santiago 🇨🇱 + Patagonia 🐧 $10,309!",
        "¡CDMX a Ginebra, Suiza $13,832!",
        "¡CDMX a San José, Costa Rica $4,382! 🐸 (Por $1,987 agrega 4 noches de hotel con desayunos)",
        "¡GDL a Lima, Perú $3,685! 🇵🇪 (Por $2,004 agrega 4 noches de hotel c/ desayunos)",
    ]

    with patch.object(Service, "_get_queue_url"):
        service = Service()
    fake_s3_message = MagicMock()

    with patch.object(service, "read_offers", return_value=offers) as read_offers_mock:
        service.process_message(fake_s3_message)

        read_offers_mock.assert_called_once_with(fake_s3_message)

    engine = get_test_engine()

    actual_offers = engine.execute(
        "SELECT id, origin, `separator`, destination, price, `text` FROM offers"
    ).fetchall()

    assert actual_offers == expected
