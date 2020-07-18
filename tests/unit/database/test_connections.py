from unittest.mock import patch, MagicMock

import pytest

from database.connections import get_connection_url


@pytest.fixture
def environ():
    return {
        "DB_DRIVERNAME": "mysql+pymysql",
        "DB_USERNAME": "VuelaX",
        "DB_PASSWORD": "Password1!",
        "DB_HOST": "localhost",
        "DB_PORT": "3366",
        "DB_DATABASE": "VuelaX",
    }


def test_get_connection_url():
    return_url = MagicMock()
    with patch("database.connections.URL", return_value=return_url) as url_patched:
        return_val = get_connection_url()

    assert return_url == return_val
    url_patched.assert_called_once_with(
        database="VuelaX",
        drivername="mysql+pymysql",
        host="localhost",
        password="Password1!",
        port="3366",
        username="VuelaX",
    )
