import os
from unittest.mock import patch
import pytest


@pytest.fixture
def environ():
    return {}


@pytest.fixture(autouse=True)
def patch_env(environ):
    def getenv(key, default=None):
        return environ.get(key, default)

    with patch.dict(os.environ, environ, clear=True):
        with patch("os.getenv", getenv):
            yield environ
