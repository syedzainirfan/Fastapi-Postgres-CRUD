from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import psycopg
from psycopg.rows import dict_row
import time

var1 = FastAPI()

# Pydantic model for request body validation
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[float] = None

# Keep trying until database connection is successful
while True:
    try:
        connection = psycopg.connect(
            host="localhost",
            dbname="Fastapi",
            user="postgres",
            password="1234",
            row_factory=dict_row
        )
        cursor = connection.cursor()
        print("Database connected successfully")
        break
    except Exception as error:
        print("Database is not connected")
        print("Error:", error)
        time.sleep(2)

# DELETE route to remove a post by id
@var1.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """DELETE FROM public.post WHERE id = %s RETURNING *""",
        (id,)
    )

    deleted_post = cursor.fetchone()

    # If no row was deleted, it means post does not exist
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )
    connection.commit()
    return
