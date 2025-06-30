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
    prefix="/admin",
    tags=["admin"]
)



def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/getallCars")
async def getallcars(db: db_dependency, user:user_dependency):
    if user is not None and user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Car).all()




@router.get("/deleteCar")
async def deleteCar(db: db_dependency, user:user_dependency, carID: int):
    if user is not None and user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    deletedCar =  db.query(Car).filter(Car.id == carID).first()
    if deletedCar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="carID not found")
    
    try:
        db.delete(deletedCar)
        db.commit()
        return {"seccuss": "car deleted"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database failure")
