from database import engine
from model import base
from fastapi import FastAPI, Request
from router import car, person, admin
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



app = FastAPI()

template = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



base.metadata.create_all(bind = engine)

app.include_router(car.router)
app.include_router(person.router)
app.include_router(admin.router)