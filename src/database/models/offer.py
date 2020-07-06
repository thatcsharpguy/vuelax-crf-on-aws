from sqlalchemy import Column, Integer, String

from database.models.base import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True)
    text = Column(String(100), nullable=False)
    destination = Column(String(100))
    separator = Column(String(100))
    origin = Column(String(100))
    price = Column(String(100))
    flag = Column(String(100))
    irrelevant = Column(String(100))
