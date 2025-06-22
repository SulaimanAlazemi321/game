import TodoApp.models
from TodoApp.database import engine
from fastapi import FastAPI

# assinging fastapi to app
app = FastAPI()


# running the app from main and create the database
TodoApp.models.Base.metadata.create_all(bind = engine)
