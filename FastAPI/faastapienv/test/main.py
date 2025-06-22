import models
from fastapi import FastAPI, Depends, Query, HTTPException, Path
from sqlalchemy.orm import session 
from database import engine, localSession
from models import todos
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Human:
    id : int
    name : str
    age : int
    hobby: str

    def __init__(self,id,  name, age, hobby):
        self.id = id
        self.name = name
        self.age = age
        self.hobby = hobby

class Get_Human(BaseModel):
     id: Optional[int] = Field(gt=0, default=None, description="you Don't need to provid ID")
     name : str = Field(min_length=1, max_length=100)
     age : int = Field(gt=0 , lt= 150)
     hobby: str = Field(min_length=3, max_length=100)

     model_config = {
         "json_schema_extra": {
             "example": {
                 "name": "Khalid",
                 "age": "20",
                 "hobby": "basketball"
             }
         }
     }

People = [
     Human(1,"Sulaiman" ,22,  "Cyber security"),
     Human(2,"ahmad" ,21,  "cars"),
     Human(3,"yousif" ,22,  "science")
    ]
models.base.metadata.create_all(bind=engine)

def get_db():
    db  = localSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_all(db: Annotated[session, Depends(get_db)]):
    return db.query(todos).all()

@app.get("/getPeople")
async def getPeople():
    return People

@app.post("/addHuman", status_code=status.HTTP_201_CREATED)
async def addbook(human: Get_Human):
    new_human = Human(**human.model_dump())
    People.append(increaseID(new_human)) 
    return {"seccsuss": f"human added with the name: {new_human.name} and ID: {new_human.id}"}

def increaseID(human: Human):
    if len(People) > 0:
        human.id = People[-1].id + 1
    else:
        human.id = 1
    return human

@app.put("/update")
async def update(human: Get_Human):
    for i in range(len(People)):
        if People[i].id == human.id:
            People[i] = human
            return People[i]
    raise HTTPException(status_code=404, detail="id not found")

@app.delete("/delete/{id}")
async def deleteHuman(id: int = Path(gt=0)):
    for i in range(len(People)):
        if People[i].id == id:
            People.pop(i)
            break
    raise HTTPException(status_code=404, detail="id not found")
            

