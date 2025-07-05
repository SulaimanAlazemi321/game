from sqlalchemy import Column,String,Boolean,Integer,ForeignKey
from model.database import base

class Customers(base):
    __tablename__ = "Customers"


    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email    = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="customer", server_default="customer")