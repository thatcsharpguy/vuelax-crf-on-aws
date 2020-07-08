import os

import boto3


def client(service):
    endpoint_url = os.getenv("AWS_ENDPOINT")
    if endpoint_url:
        return boto3.client(service, endpoint_url=endpoint_url)
    return boto3.client(service)
