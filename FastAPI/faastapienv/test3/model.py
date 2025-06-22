from database import base
from sqlalchemy import Column, String, Integer, Boolean



class People(base):
    __tablename__ = "People"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    description = Column(String)