from model import base, People
from sqlalchemy.exc import SQLAlchemyError
from database import engine, local_session
from fastapi import FastAPI, Depends, HTTPException, Query, Path
from starlette import status
from pydantic import Field, BaseModel
from typing import Annotated, Optional
from sqlalchemy.orm import session

# class book:
#     id : int
#     title : str
#     description : str

#     def __init__(self, id, title, description):
#         self.id = id
#         self.title = title
#         self.description = description

class BookSchema (BaseModel):
    id : Optional[int] = Field(gt=-1, default=None, description="this is not required")
    title : str = Field(min_length= 1 , max_length=100)
    description : str = Field(min_length=3 , max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "the title",
                "description": "the description"
            }
        }
    }


class PersonSchema(BaseModel):
    name: str = Field(min_length=1 , max_length=100)
    age: int = Field(gt = 0 , lt = 200)
    description: Optional[str] = Field(min_length=2, max_length=100, default=None)


    model_config = {
            "json_schema_extra": {  
                "example": {
                    "name": "the name",
                    "age": 20,
                    "description" : "your description"
                }
            }
        }


app = FastAPI()
base.metadata.create_all(bind = engine)
books = [
    BookSchema (id = 1,title = "test1", description = "Test1"),
    BookSchema (id =2,title ="test2",  description ="Test2"),
    BookSchema (id =3,title ="test3",  description ="Test3"),
    BookSchema (id =4,title ="test4",  description ="Test4")
]




def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def getbook(db: session = Depends(get_db)):
    answer = db.query(People).all()
    return answer

@app.get("/books")
async def getallbooks():
    return books


@app.post("/addBook", status_code= status.HTTP_201_CREATED)
async def addbook(book1: BookSchema ):
    books.append(add_id(book1))
    return {"Item added with title": f"{book1.title}"}


def add_id(book: BookSchema ):
    if len(books) > 0:
        book.id = books[-1].id + 1
    else:
        book.id = 1
    return book


@app.get("/getBookByID/{bookID}", status_code= status.HTTP_200_OK)
async def getbookByID(bookID : int = Path(gt=0)):
    for book in books:
        if book.id == bookID:
            return book
    raise HTTPException(status_code=404, detail="BookID not found")




@app.delete("/bookDeletebyID/", status_code=status.HTTP_200_OK)
async def deleteBookByID(bookID : int = Query(gt=0)):
    for i in range(len(books)):
        if books[i].id == bookID: 
            return {"Seccuss": f"Item removed with ID {books.pop(i).id}"}
    raise HTTPException(status_code= 404, detail="Book ID not found")


@app.get("/getbooksFromDB")
async def getbookfromDB(db : session = Depends(get_db)):
    return db.query(People).all()

@app.post("/addingPeople", status_code=status.HTTP_201_CREATED)
def addingbooks(person : PersonSchema, db : session = Depends(get_db)):
    try:      
        db.add(People(**person.model_dump()))
        db.commit()
        return {"Seccuss": "person added"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(code = 500, detail= "database failed ")








