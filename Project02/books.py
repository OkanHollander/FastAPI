from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
    book_id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, book_id, title, author, description, rating, published_date):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    book_id: Optional[int] = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'Dramaqueen',
                'description': 'A new description',
                'rating': 5,
                'published_date': 2016
            }
        }

BOOKS = [
    Book(1, "Computer Science Pro", "Dramaqueen", "A very nice book!", 5, 2011),
    Book(2, "Be Fast With FastAPI", "Dramaqueen", "A great book", 5, 2012),
    Book(3, "Master Endpoints", "Dramaqueen", "An awesome book", 5, 2013),
    Book(4, "HP1", "Dramaqueen", "Book description", 3, 2014),
    Book(5, "HP2", "Dramaqueen", "Book description", 2, 2015),
    Book(6, "HP3", "Dramaqueen", "Book description", 1, 2016),
]

# find book id
def find_book_id(book: Book):
    book.book_id = 1 if len(BOOKS) == 0 else BOOKS[-1].book_id + 1
    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i, b in enumerate(BOOKS):
        if b.book_id == book.book_id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i, b in enumerate(BOOKS):
        if b.book_id == book_id:
            BOOKS.pop(i)
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.book_id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/published/", status_code=status.HTTP_200_OK)
async def read_book_by_year_published(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    