from datetime import datetime
import json
from unittest.mock import patch

import backoff
import boto3
import pytest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError

from database.models.base import Base
from database.models.offer import Offer


@pytest.fixture
def environ(docker_ip):
    return {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_DEFAULT_REGION": "eu-west-2",
        "AWS_REGION": "eu-west-2",
        "AWS_SECRET_ACCESS_KEY": "test",
        "DB_DRIVERNAME": "mysql+pymysql",
        "DB_USERNAME": "VuelaX",
        "DB_PASSWORD": "Password1!",
        "DB_HOST": docker_ip,
        "DB_PORT": "3306",
        "DB_DATABASE": "VuelaX",
    }


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    docker_fixtures_path = Path(pytestconfig.rootdir, "tests", "docker")
    return Path(docker_fixtures_path, "end-to-end.yml")


@pytest.fixture
def bucket_name():
    return "vuelax-landing-bucket"


@pytest.fixture
def queue_name():
    return "vuelax-landing-queue"


@pytest.fixture(scope="session")
def localstack_endpoint(docker_ip):
    return f"http://{docker_ip}:4566"


@pytest.fixture
def get_boto_client(docker_ip, docker_services):
    def _inner(service):
        boto3.setup_default_session()

        client = boto3.client(
            service_name=service, endpoint_url=f"http://{docker_ip}:4566",
        )

        return client

    return _inner


@pytest.fixture
def sqs_client(get_boto_client):
    return get_boto_client("sqs")


@pytest.fixture
def s3_client(get_boto_client):
    return get_boto_client("s3")


@pytest.fixture
def setup_localstack(
    get_boto_client, docker_services, s3_client, sqs_client, bucket_name, queue_name
):
    def swallow_exceptions(function, exceptions=Exception):
        def _test():
            try:
                function()
                return True
            except exceptions:
                return False

        return _test

    docker_services.wait_until_responsive(
        timeout=60.0, pause=0.1, check=swallow_exceptions(s3_client.list_buckets)
    )

    s3_client.create_bucket(Bucket=bucket_name)

    docker_services.wait_until_responsive(
        timeout=60.0, pause=0.1, check=swallow_exceptions(sqs_client.list_queues)
    )

    sqs_client.create_queue(QueueName=queue_name)
    yield


@pytest.fixture
def send_message(setup_localstack, sqs_client, queue_name):
    queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]

    def _send_message(message_body):
        if not isinstance(message_body, str):
            message_body = json.dumps(message_body)
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)

    return _send_message


@pytest.fixture
def upload_file(s3_client, send_message, bucket_name):
    basic_s3_message_skeleton = {
        "Records": [
            {
                "eventTime": None,
                "eventName": "s3:ObjectCreated:*",
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "bucket": {"name": bucket_name,},
                    "object": {"key": None,},
                },
            }
        ]
    }

    def _upload_file(file, key=None):
        key = key or file.name
        basic_s3_message_skeleton["Records"][0][
            "eventTime"
        ] = datetime.now().isoformat()

        basic_s3_message_skeleton["Records"][0]["s3"]["object"]["key"] = key
        with open(file, "rb") as fd:
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=fd)
        send_message(basic_s3_message_skeleton)
        return basic_s3_message_skeleton

    return _upload_file


@pytest.fixture
def input_file(pytestconfig):
    return Path(pytestconfig.rootdir, "tests", "fixtures", "input.txt")


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


def test_run(
    start_db,
    setup_localstack,
    get_test_engine,
    input_file,
    send_message,
    sqs_client,
    s3_client,
    upload_file,
):
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

    upload_file(input_file)

    @backoff.on_exception(
        backoff.constant, interval=3, exception=Exception, max_time=60
    )
    def assert_inserted_records():
        engine = get_test_engine()
        items = engine.execute(
            "SELECT id, origin, `separator`, destination, price, `text` FROM offers"
        ).fetchall()
        assert items == expected

    assert_inserted_records()
