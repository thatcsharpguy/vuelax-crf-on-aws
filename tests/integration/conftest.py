import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    docker_fixtures_path = Path(pytestconfig.rootdir, "tests", "docker")
    return Path(docker_fixtures_path, "integration.yml")
