from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

database_uri = "sqlite:///./database.db"



engine = create_engine(database_uri, connect_args={'check_same_thread':False})

creating_local_session = sessionmaker(autoflush=False, autocommit = False, bind=engine)

base = declarative_base()