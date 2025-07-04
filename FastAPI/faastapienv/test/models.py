from database import base
from sqlalchemy import Column, String, Integer, Boolean

class todos(base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key= True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean)
