from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# the place where the database will be created 
SQLalchemy_DataBase_URL = 'sqlite:///./todos.db'

#creating the engine to be used later
engine = create_engine(SQLalchemy_DataBase_URL, connect_args={'check_same_thread':False})

# opening local session and preventing auto flush, commet then connecting it to the engine 
localSession = sessionmaker(autoflush=False, autocommit = False, bind=engine)

# the assigning the variable base as declarative_base to be used in the models.py
Base = declarative_base()

