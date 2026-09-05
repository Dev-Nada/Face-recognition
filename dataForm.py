from Db import get_connection
import numpy as np


def tables():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE,
            city TEXT NOT NULL,
            face_embedding BLOB NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    """)

    connection.commit()
    connection.close()

def add_employee(name, age, email, city, embedding, created_at):

    connection = get_connection()
    cursor = connection.cursor()

    embedding_bytes = embedding.astype(np.float32).tobytes()

    cursor.execute("""
        INSERT INTO employees
        (name, age, email, city, face_embedding, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        email,
        city,
        embedding_bytes,
        created_at
    ))

    employee_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return employee_id