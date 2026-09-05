from datetime import datetime
from fastapi import APIRouter, HTTPException

from Db import get_connection

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in/{employee_id}")
def check_in(employee_id: int):
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ?", (employee_id,))
        employee = cursor.fetchone()

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        cursor.execute(
            "SELECT id FROM attendance WHERE employee_id = ? AND check_out IS NULL",
            (employee_id,)
        )
        open_record = cursor.fetchone()

        if open_record is not None:
            raise HTTPException(status_code=409, detail="Employee already checked in")

        check_in_time = datetime.now().isoformat()

        cursor.execute(
            "INSERT INTO attendance (employee_id, check_in) VALUES (?, ?)",
            (employee_id, check_in_time)
        )
        connection.commit()
        record_id = cursor.lastrowid

        return {
            "success": True,
            "message": "Checked in",
            "id": record_id,
            "check_in": check_in_time
        }
    finally:
        connection.close()


@router.post("/check-out/{employee_id}")
def check_out(employee_id: int):
    connection = get_connection()
    try:
        cursor = connection.cursor()

        
        cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ?", (employee_id,))
        employee = cursor.fetchone()

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        cursor.execute(
            "SELECT id FROM attendance WHERE employee_id = ? AND check_out IS NULL ORDER BY id DESC LIMIT 1",
            (employee_id,)
        )
        open_record = cursor.fetchone()

        if open_record is None:
            raise HTTPException(status_code=404, detail="No open check-in found")

        check_out_time = datetime.now().isoformat()

        cursor.execute(
            "UPDATE attendance SET check_out = ? WHERE id = ?",
            (check_out_time, open_record["id"])
        )
        connection.commit()

        return {
            "success": True,
            "message": "Checked out",
            "id": open_record["id"],
            "check_out": check_out_time
        }
    finally:
        connection.close()


@router.get("/{employee_id}")
def get_attendance(employee_id: int):
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT id, employee_id, check_in, check_out FROM attendance WHERE employee_id = ?", (employee_id,))
        records = cursor.fetchall()

        return [
            {
                "id": r["id"],
                "employee_id": r["employee_id"],
                "check_in": r["check_in"],
                "check_out": r["check_out"]
            }
            for r in records
        ]
    finally:
        connection.close()