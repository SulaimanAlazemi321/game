from database import localSession
from sqlalchemy.orm import session
from sqlalchemy.exc import SQLAlchemyError
from model import Person
from fastapi import APIRouter, Path, Query, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta

pass_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/person",
    tags=["Person"]
)

ALGORITHM = "HS256"
SECRET_KEY = "LoveBarrnyIsRealOhhSOOGOOD"
auth_bearer = OAuth2PasswordBearer(tokenUrl="person/token")


class Token(BaseModel):
    access_token : str
    token_type : str

class personSchema(BaseModel):
    email: str = Field(min_length=4)
    name: str = Field(min_length=2)
    age: int = Field(gt=0)
    password: str
    isActive: Optional[bool] = True
    role: str

    model_config = {
            "json_schema_extra": {
                "example": {
                    "email": "sulaiman@example.com",
                    "name": "Sulaiman",
                    "age": 25,
                    "password": "hashed_password_here",
                    "isActive": True,
                    "role": "admin"
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


@router.get("/getAllpersons")
async def getAllData(db : db_dependency):
    return db.query(Person).all()


@router.get("/getpersonByID/{personID}")
async def getpersonByID(db : db_dependency, personID : int = Path(gt=0)):
    person =  db.query(Person).filter(personID == Person.id).first()
    if person:
        return person
    elif not person:
        raise HTTPException(status_code=404, detail="person ID not found")
    else:
        raise HTTPException(status_code=500, detail="something went wrong ")
    


@router.post("/addperson", status_code = status.HTTP_201_CREATED)
async def addPerson(db: db_dependency, person: personSchema):
    try:
        new_data = Person(
            email = person.email,
            name = person.name,
            age = person.age,
            hashPassword = pass_hasher.hash(person.password),
            isActive = person.isActive,
            role = person.role
        )
        db.add(new_data)
        db.commit()
        return {"Seccuss": "person added"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database failur")



@router.put("/updateperson/")
async def updateDataByID(db : db_dependency, person : personSchema, personID : int = Query(gt=0)):
    foundperson = db.query(Person).filter(personID == Person.id).first()

    if foundperson:
        foundperson.email = person.email
        foundperson.name = person.name
        foundperson.age = person.age
        foundperson.hashPassword = pass_hasher.hash(person.password)
        foundperson.isActive = person.isActive
        foundperson.role = person.role


        db.add(foundperson)
        db.commit()
        return {"seccuss": "person updated"}
    
    raise HTTPException(status_code=404, detail="person ID not found")


@router.delete("/Deleteperson/{personID}")
async def deleteperson(db: db_dependency, personID : int):
    foundperson = db.query(Person).filter(Person.id == personID).first()
    if foundperson:
        db.delete(foundperson)
        db.commit()
        return {"seccuss": "person deleted"}
    
    raise HTTPException(status_code=404, detail="person id not found")



def authenticateHelper(username: str, password: str, db):
    person = db.query(Person).filter(username == Person.name).first()
    if person and pass_hasher.verify(password, person.hashPassword):
        return person
    return False


@router.post("/authenticate-user", response_model=Token)
async def authenticateUser(db: db_dependency, from_data : Annotated[OAuth2PasswordRequestForm, Depends()]):
    user  = authenticateHelper(username=from_data.username, password=from_data.password, db=db)
    if user:
        token = generateToken(username=user.name, id=user.id, deltatime=timedelta(minutes=20))
        return {"access_token": token,"token_type": "bearer" }
    else:
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not valid jwt")


def generateToken(username : str, id : str , deltatime: timedelta):
    expire = datetime.now(timezone.utc) + deltatime
    encode = {"sub": username, "id": id, "expire":expire.isoformat()}
    return jwt.encode(algorithm=ALGORITHM, key=SECRET_KEY, claims=encode)


def tokenDecode(token : Annotated[str, Depends(auth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        userID = payload.get("id")
        if not username or not userID:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not valid jwt")
        
        return {"username": username, "id": userID}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not valid jwt")
        