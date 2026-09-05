from fastapi import APIRouter, HTTPException
from Db import get_connection

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/{identifier}")
def get_employee(identifier: str):
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT employee_id, name, age, email, city, created_at 
            FROM employees 
            WHERE employee_id = ? OR email = ? OR name = ?
            """,
            (identifier, identifier, identifier)
        )
        employee = cursor.fetchone()

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {
            "employee_id": employee["employee_id"],
            "name": employee["name"],
            "age": employee["age"],
            "email": employee["email"],
            "city": employee["city"],
            "created_at": employee["created_at"]
        }
    finally:
        connection.close()