from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

dataBaseURI = "sqlite:///./carApp.db"

engine = create_engine(dataBaseURI, connect_args={"check_same_thread": False})

localSession = sessionmaker(autoflush=False, autocommit = False, bind= engine)

base = declarative_base()