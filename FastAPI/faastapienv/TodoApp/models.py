from TodoApp.database import Base
from sqlalchemy import Column, String, Boolean, Integer

#creating a class and inheret from base
class Todos(Base):
    # naming the database todos
    __tablename__ = "todos"

    # creating the attributes of the database
    id = Column(Integer, primary_key= True, index= True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
