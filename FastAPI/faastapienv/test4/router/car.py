from database import localSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model import Car
from fastapi import APIRouter, Path, Query, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from router.person import get_current_user



user_dependency = Annotated[dict, Depends(get_current_user)]




router = APIRouter(
    prefix="/Car",
    tags=["Car"]
)


@router.get("/testing123")
def usertest(user: user_dependency, name : str):
    name1 = name
    if user != None:
        return {"username": user.get('username'), "id": user.get('id')}
    else:
        "authenticate first please"


class carSchema(BaseModel):
    factory : str = Field(min_length=1, max_length=100)
    model : int = Field(lt=2027, gt= 1900)
    isEcoFrindly : bool 
    model_config = {
        "json_schema_extra": {
            "example": {
                "factory": "Toyota",
                "model": 2010,
                "isEcoFrindly": True,

            }
        }
    }

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/getAllCars")
async def getAllData(db : db_dependency):
    return db.query(Car).all()


@router.get("/getAllMyCars/")
async def getCarByID(db : db_dependency,user: user_dependency):
    car =  db.query(Car).filter(user.get("id") == Car.person).all()
    
    if car:
        return car
    elif not car:
        raise HTTPException(status_code=404, detail="car ID not found")
    else:
        raise HTTPException(status_code=500, detail="something went wrong ")
    


@router.post("/addCar", status_code = status.HTTP_201_CREATED)
async def addData(db: db_dependency, car: carSchema, user: user_dependency):
    try:
        new_data = Car(**car.model_dump(), person = user.get("id"))
        db.add(new_data)
        db.commit()
        return {"Seccuss": "Car added"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database failur")



@router.put("/updateCar/")
async def updateDataByID(db : db_dependency, car : carSchema, carID : int = Query(gt=0)):
    foundCar = db.query(Car).filter(carID == Car.id).first()

    if foundCar:
        foundCar.model = car.model
        foundCar.factory = car.factory
        foundCar.isEcoFrindly = car.isEcoFrindly


        db.add(foundCar)
        db.commit()
        return {"seccuss": "car updated"}
    
    raise HTTPException(status_code=404, detail="car ID not found")


@router.delete("/DeleteCar/{carID}")
async def deleteCar(db: db_dependency, carID : int):
    foundcar = db.query(Car).filter(Car.id == carID).first()
    if foundcar:
        db.delete(foundcar)
        db.commit()
        return {"seccuss": "car deleted"}
    
    raise HTTPException(status_code=404, detail="car id not found")

