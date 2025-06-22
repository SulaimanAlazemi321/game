from sqlalchemy import Column, Integer, String, Boolean
from database import base


class database(base):
   __tablename__ = "theD"
   id = Column(Integer, primary_key=True, index=True)
   title = Column(String)
   description = Column(String)
   done = Column(Boolean)