from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from database import base

class Car(base):
    __tablename__ = "car"
    id = Column(Integer, primary_key=True, index=True)
    factory = Column(String)
    model = Column(Integer)
    isEcoFrindly = Column(Boolean)
    person = Column(Integer, ForeignKey("Person.id"))


class Person(base):
    __tablename__ = "Person"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    name = Column(String, unique=True)
    age = Column(Integer)
    hashPassword = Column(String)
    isActive = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

       

