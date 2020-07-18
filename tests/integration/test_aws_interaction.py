import json
import os
from pathlib import Path
from unittest.mock import patch

import boto3
import pytest

from main import run, process_s3_message
from datetime import datetime


@pytest.fixture
def bucket_name():
    return "vuelax-landing-bucket"


@pytest.fixture
def queue_name():
    return "vuelax-landing-queue"


@pytest.fixture
def localstack_endpoint(docker_ip):
    return f"http://{docker_ip}:4566"


@pytest.fixture
def environ(localstack_endpoint, queue_name):
    return {
        "QUEUE_NAME": queue_name,
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_DEFAULT_REGION": "eu-west-2",
        "AWS_REGION": "eu-west-2",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_ENDPOINT": localstack_endpoint,
    }


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


def test_run(
    setup_localstack, input_file, send_message, sqs_client, s3_client, upload_file
):
    with open(input_file) as fd:
        expected_lines = [line.strip() for line in fd.readlines()]
    sent_body = upload_file(input_file)
    with patch("main.execute") as execute_patched:
        process_s3_message(sent_body)

        execute_patched.assert_called_once_with(expected_lines)
