from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
from typing import Optional

var1 = FastAPI()

# Database connection URL
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/Fastapi"

# Database connection management
def get_db_connection():
    try:
        connection = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        return connection
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Database connection error: {error}")

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[float] = None

@var1.post("/Createpost", status_code=201)
def create_post(post: Post, connection: psycopg.Connection = Depends(get_db_connection)):
    try:
        # Use cursor in context to ensure it is closed after execution
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.post (title, content, published, rating) 
                VALUES (%s, %s, %s, %s) RETURNING id, title, content, published, rating;
            """, (post.title, post.content, post.published, post.rating))

            new_post = cursor.fetchone()
            connection.commit()

        if new_post:
            return {"Data": new_post}
        else:
            raise HTTPException(status_code=400, detail="Failed to create the post")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error creating post: {error}")
