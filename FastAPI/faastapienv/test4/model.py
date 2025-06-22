from sqlalchemy import Column, String, Integer, Boolean
from database import base

class Car(base):
    __tablename__ = "car"
    id = Column(Integer, primary_key=True, index=True)
    factory = Column(String)
    model = Column(Integer)
    isEcoFrindly = Column(Boolean)