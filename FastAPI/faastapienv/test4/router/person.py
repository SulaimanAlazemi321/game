from database import localSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model import Person
from fastapi import APIRouter, Path, Query, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from typing import Optional, Annotated
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from sqlalchemy import text

template = Jinja2Templates(directory="templates")
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
    phone_number : str

    model_config = {
            "json_schema_extra": {
                "example": {

                    "email": "sulaiman@example.com",
                    "name": "Sulaiman",
                    "age": 25,
                    "password": "hashed_password_here",
                    "isActive": True,
                    "role": "admin",
                    "phone_number":  "51590622"
                }
            }
        }
 
Jinja2Templates

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    age: int
    isActive: bool
    role: str


def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


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
async def access_tokenaddPerson(db: db_dependency, person: personSchema):
    try:
        new_data = Person(
            email = person.email,
            name = person.name,
            age = person.age,
            hashPassword = pass_hasher.hash(person.password),
            isActive = person.isActive,
            role = person.role,
            phone_number = person.phone_number
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

    if not foundperson:
        raise HTTPException(status_code=404, detail="person ID not found")
    name_conflict = db.query(Person).filter(Person.name == person.name, Person.id != personID).first()
    email_conflict = db.query(Person).filter(Person.email == person.email, Person.id != personID).first()

    if name_conflict:
        raise HTTPException(status_code=400, detail="Name already exists")
    if email_conflict:
        raise HTTPException(status_code=400, detail="Email already exists")
   
    foundperson.email = person.email
    foundperson.name = person.name
    foundperson.age = person.age
    foundperson.hashPassword = pass_hasher.hash(person.password)
    foundperson.isActive = person.isActive
    foundperson.role = person.role
    foundperson.phone_number = person.phone_number


    db.add(foundperson)
    db.commit()
    return {"seccuss": "person updated"}
    
    


@router.delete("/Deleteperson/{personID}")
async def deleteperson(db: db_dependency, personID : int):
    foundperson = db.query(Person).filter(Person.id == personID).first()
    if foundperson:
        db.delete(foundperson)
        db.commit()
        return {"seccuss": "person deleted"}
    
    raise HTTPException(status_code=404, detail="person id not found")



'''
4 functions that I need
1- authenticate helper -> bool or user
2- jwt encode -> jwt
3- authenticate to use function 1 - 2
4- jwt decode
'''


def authenticate_helper(username : str, password: str, db):
    user = db.query(Person).filter(username == Person.name).first()
    if user and pass_hasher.verify(password, user.hashPassword):
        return user
    else:
        return False
    


def jwtGenerate(username: str, id: int, role: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=2000)
    encode = {"sub": username, "id": id, "role": role, "expire": expire.isoformat()}
    jwt_token = jwt.encode(algorithm=ALGORITHM, key=SECRET_KEY,claims=encode)
    return jwt_token

@router.post("/token", response_model=Token)
async def get_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_helper(form_data.username, form_data.password, db)
    if user:
        jwt_token = jwtGenerate(user.name, user.id, user.role)
        return {"access_token": jwt_token, "token_type": "Bearer"}
    elif user == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid credintial")
    


def get_current_user(token : Annotated[str, Depends(auth_bearer)]):
    try:
        jwt_token = jwt.decode(token=token, algorithms=ALGORITHM, key=SECRET_KEY)
        username = jwt_token.get("sub") 
        id = jwt_token.get("id") 
        role = jwt_token.get("role")
        if not username or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/whoami", response_model=UserOut, status_code=200)
async def whoami(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    foundUser = db.query(Person).filter(Person.id == user.get('id')).first()

    if foundUser is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    return foundUser
        


@router.put("/updatePassword", status_code=status.HTTP_204_NO_CONTENT)

async def updatePassword(db: db_dependency, user: user_dependency, newPassword: str):
    theUser = db.query(Person).filter(Person.id == user.get("id")).first()

    if theUser is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    theUser.hashPassword =  pass_hasher.hash(newPassword)
    db.commit()



@router.put("/update-phone-number")
def update_phone_number(user : user_dependency, db : db_dependency, newNumber : str):
    theUser = db.query(Person).filter(user.get("id") == Person.id).first()
    if theUser:
        theUser.phone_number = newNumber
        db.commit()
        return "succuss"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

#pages  

@router.get("/login")
async def login(request: Request):
    return template.TemplateResponse("login.html", {"request": request})

@router.get("/home")
async def test(request : Request):
    return template.TemplateResponse("home.html", {"request": request})



