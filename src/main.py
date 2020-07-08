import json
import logging
import os

import backoff
from smart_open import open as smart_open

from database.connections import get_session
from database.models.offer import Offer
from local_boto import client
from tagger import Tagger


def read_offers(file):
    s3_client = client("s3")
    with smart_open(
        file,
        "r",
        transport_params={
            "resource_kwargs": {"endpoint_url": s3_client.meta.endpoint_url},
        },
    ) as external:
        return [line.strip() for line in external]


def store_offers(offers, predicted_labels):
    with get_session() as session:
        for offer, labels in zip(offers, predicted_labels):
            session.add(Offer(text=offer, **labels))


@backoff.on_exception(backoff.expo, exception=Exception)
def get_queue_url(sqs_client, queue_name):
    return sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]


def run():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.info("starting service")
    while True:
        try:
            logger.info("starting service")
            queue_name = os.environ["QUEUE_NAME"]
            sqs_client = client("sqs")
            queue_url = get_queue_url(sqs_client, queue_name)
            response = sqs_client.receive_message(
                QueueUrl=queue_url, WaitTimeSeconds=20
            )
            for message in response.get("Messages", list()):
                s3_message = json.loads(message["Body"])
                process_s3_message(s3_message)
                sqs_client.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
                )
        except Exception as e:
            logger.exception("bad!")


def process_s3_message(s3_message):
    for record in s3_message["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        offers = read_offers(f"s3://{bucket}/{key}")
        execute(offers)


def execute(offers):
    tagger = Tagger("vuelax.pkl")
    predicted_labels = tagger.tag(offers)
    store_offers(offers, predicted_labels)


if __name__ == "__main__":
    run()
