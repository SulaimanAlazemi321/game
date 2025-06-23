from database import localSession
from sqlalchemy.orm import session
from sqlalchemy.exc import SQLAlchemyError
from model import Car
from fastapi import APIRouter, Path, Query, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Annotated

router = APIRouter()


class carSchema(BaseModel):
    factory : str = Field(min_length=1, max_length=100)
    model : int = Field(lt=2027, gt= 1900)
    isEcoFrindly : bool 
    person : Optional[int] = Field(gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "factory": "Toyota",
                "model": 2010,
                "isEcoFrindly": True,
                "person": 1
            }
        }
    }

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session, Depends(get_db)]


@router.get("/getAllCars")
async def getAllData(db : db_dependency):
    return db.query(Car).all()


@router.get("/getCarByID/{carID}")
async def getCarByID(db : db_dependency, carID : int = Path(gt=0)):
    car =  db.query(Car).filter(carID == Car.id).first()
    if car:
        return car
    elif not car:
        raise HTTPException(status_code=404, detail="car ID not found")
    else:
        raise HTTPException(status_code=500, detail="something went wrong ")
    


@router.post("/addCar", status_code = status.HTTP_201_CREATED)
async def addData(db: db_dependency, car: carSchema):
    try:
        new_data = Car(**car.model_dump())
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

