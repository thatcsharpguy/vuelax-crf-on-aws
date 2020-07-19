import json
import logging
import os

import backoff
from smart_open import open as smart_open

from database.connections import get_session
from database.models.offer import Offer
from local_boto import client
from tagger import Tagger


class Service:
    def __init__(self):
        self.sqs_client = client("sqs")
        self.s3_client = client("s3")
        self.queue_url = self._get_queue_url(os.environ["QUEUE_NAME"])
        self.tagger = Tagger("vuelax.pkl")

    @backoff.on_exception(backoff.expo, exception=Exception)
    def _get_queue_url(self, queue_name):
        """
        Get the queue url for a given queue name.
        This method has `backoff` enabled so that it does not fail right away if the queue does not exist.
        :param queue_name:
        :return:
        """
        return self.sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]

    def run(self):
        """
        Reads constantly from an SQS queue polling from messages to be processed
        """
        while True:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url, WaitTimeSeconds=20
            )
            for message in response.get("Messages", list()):
                s3_message = json.loads(message["Body"])
                self.process_message(s3_message)
                self.sqs_client.delete_message(
                    QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"]
                )

    def store_offers(self, offers, predicted_labels):
        """
        Save the tagged offers in the database
        :param offers: A list of strings, where each string is an offer
        :param predicted_labels: A list of tags corresponding to each offer in :offers:
        """
        with get_session() as session:
            for offer, labels in zip(offers, predicted_labels):
                session.add(Offer(text=offer, **labels))

    def read_offers(self, s3_message):
        """
        Reads offers from an s3 file
        :param bucket:
        :param key:
        :return: The lines inside the file
        """
        offers_in_file = []

        for record in s3_message["Records"]:
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]
            with smart_open(
                f"s3://{bucket}/{key}",
                "r",
                transport_params={
                    "resource_kwargs": {
                        "endpoint_url": self.s3_client.meta.endpoint_url
                    },
                },
            ) as external:
                offers_in_file.extend([line.strip() for line in external])

        return offers_in_file

    def process_message(self, s3_message):
        """
        Process an s3 message by reading the file to be processed from s3, tagging the offers and then storing them in the database
        :param s3_message:
        """
        offers = self.read_offers(s3_message)
        predicted_labels = self.tagger.tag(offers)
        self.store_offers(offers, predicted_labels)


if __name__ == "__main__":
    service = Service()
    service.run()
