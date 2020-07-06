from contextlib import contextmanager

from database.connections import get_session
from database.models.base import Base
from database.models.offer import Offer
from tagger import Tagger


def execute():
    tagger = Tagger("vuelax.pkl")

    offers = [
        "¡CDMX a Santiago 🇨🇱 + Patagonia 🐧 $10,309!",
        "¡CDMX a Ginebra, Suiza $13,832!",
        "¡CDMX a San José, Costa Rica $4,382! 🐸 (Por $1,987 agrega 4 noches de hotel con desayunos)",
    ]

    predicted_labels = tagger.tag(offers)

    with get_session() as session:
        for offer, labels in zip(offers, predicted_labels):
            session.add(Offer(text=offer, **labels))
