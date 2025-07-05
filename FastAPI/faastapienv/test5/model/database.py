from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 

database_URI = "sqlite:///./mainStore.db"

engine = create_engine(database_URI, connect_args={"check_same_thread": False})
local_session = sessionmaker(autoflush=False, autocommit = False, bind=engine)
base = declarative_base()