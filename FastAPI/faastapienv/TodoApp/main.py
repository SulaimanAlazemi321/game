import TodoApp.models
from TodoApp.database import engine
from fastapi import FastAPI

app = FastAPI()

TodoApp.models.Base.metadata.create_all(bind = engine)
