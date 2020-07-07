from contextlib import contextmanager

from database.connections import get_session
from database.models.base import Base
from database.models.offer import Offer
from tagger import Tagger


def read_offers():
    pass


def store_offers(offers, predicted_labels):
    with get_session() as session:
        for offer, labels in zip(offers, predicted_labels):
            session.add(Offer(text=offer, **labels))


def execute():

    tagger = Tagger("vuelax.pkl")

    offers = read_offers()

    predicted_labels = tagger.tag(offers)

    store_offers(offers, predicted_labels)
