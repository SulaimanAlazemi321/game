from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Database_URL = "sqlite:///./test.db"

engine = create_engine(Database_URL, connect_args={'check_same_thread': False} )

localSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

base = declarative_base()