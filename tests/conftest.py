import os
from unittest.mock import patch
import pytest


@pytest.fixture
def environment():
    return {}


@pytest.fixture(autouse=True)
def patch_env(environment):
    def getenv(key, default=None):
        return environment.get(key, default)

    with patch.dict(os.environ, environment):
        with patch("os.getenv", getenv):
            yield environment
