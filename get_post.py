from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager

var1 = FastAPI()

# Database connection settings
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/Fastapi"

# Database connection management using context manager
@contextmanager
def get_db_connection():
    try:
        connection = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        yield connection
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Database connection error: {error}")
    finally:
        if connection:
            connection.close()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[float] = None

@var1.get("/post/{id}", status_code=200)
def get_post(id: int, db: psycopg.Connection = Depends(get_db_connection)):
    """
    Fetch a post by ID from the database.
    If not found, returns HTTP 404 error.
    """
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM public.post WHERE id = %s", (id,))
            post = cursor.fetchone()
            
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
                
            return {"Post": post}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error fetching post: {error}")
