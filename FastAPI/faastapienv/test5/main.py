from model.database import engine
from model.model import base
from fastapi import FastAPI
from routes import customer
from fastapi.staticfiles import StaticFiles

app = FastAPI()

base.metadata.create_all(bind = engine)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(customer.router)

