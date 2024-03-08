from fastapi import FastAPI

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


BOOKS = [
    Book(1, "Computer Science Pro", "Dramaqueen", "A very nice book!", 5),
    Book(2, "Be Fast With FastAPI", "Dramaqueen", "A great book", 5),
    Book(3, "Master Endpoints", "Dramaqueen", "An awesome book", 5),
    Book(4, "HP1", "Dramaqueen", "Book description", 3),
    Book(5, "HP2", "Dramaqueen", "Book description", 2),
    Book(6, "HP3", "Dramaqueen", "Book description", 1),
]

@app.get("/books")
async def read_all_books():
    return BOOKS
