from fastapi import FastAPI, Response, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import psycopg
from psycopg.rows import dict_row
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[float]

def get_db_connection():
    try:
        connection = psycopg.connect(
            host="localhost", dbname="Fastapi", user="postgres", password="1234", row_factory=dict_row
        )
        return connection
    except Exception as error:
        print("Database connection failed:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/post/{id}")
def update_post(id: int, post: Post):
    # Establish the connection to the database
    connection = get_db_connection()
    try:
        # Create a cursor
        cursor = connection.cursor()

        # Execute the update query
        cursor.execute(
            """UPDATE public.post SET title = %s, content = %s WHERE id = %s RETURNING *""",
            (post.title, post.content, id),
        )

        # Fetch the updated post
        updated_post = cursor.fetchone()

        # If no post is found with the given id, raise an exception
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Commit the transaction
        connection.commit()

        # Return the updated post
        return {"data": updated_post}
    except Exception as error:
        # Handle any database or execution errors
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {error}")
    finally:
        # Ensure the connection is closed after operation
        connection.close()
