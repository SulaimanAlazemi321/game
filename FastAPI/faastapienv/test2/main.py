from models import base
from database import engine
from fastapi import FastAPI

app = FastAPI()


base.metadata.create_all(bind = engine)

