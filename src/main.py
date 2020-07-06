from contextlib import contextmanager

from models import Base
from models.offer import Offer
from tagger import Tagger

tagger = Tagger("vuelax.pkl")

offers = [
    "¡CDMX a Santiago 🇨🇱 + Patagonia 🐧 $10,309!",
    "¡CDMX a Ginebra, Suiza $13,832!",
    "¡CDMX a San José, Costa Rica $4,382! 🐸 (Por $1,987 agrega 4 noches de hotel con desayunos)",
]


tags = tagger.tag(offers)


from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:', echo=True)

Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

@contextmanager
def get_sess():
    sess = Session()
    yield sess
    sess.commit()

with get_sess() as sess:
    sess.add(Offer(text = offers[0], **tags[0]))

with get_sess() as sess:
    all = sess.query(Offer).all()
    import pdb; pdb.set_trace()
    pass