from database import engine
from model import base
from fastapi import FastAPI
from router import car, person, admin


app = FastAPI()
base.metadata.create_all(bind = engine)

app.include_router(car.router)
app.include_router(person.router)
app.include_router(admin.router)