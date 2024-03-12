from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

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
    published_date: int = Field(gt=0)

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

@app.put("/books/update_book")
async def update_book(book: BookRequest):
    for i, b in enumerate(BOOKS):
        if b.book_id == book.book_id:
            BOOKS[i] = book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i, b in enumerate(BOOKS):
        if b.book_id == book_id:
            BOOKS.pop(i)

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.book_id == book_id:
            return book

@app.get("/books/")
async def read_book_by_rating(rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/published/")
async def read_book_by_year_published(published_date: int):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    