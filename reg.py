import sqlite3
from datetime import datetime
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from model import get_face_embedding
from dataForm import add_employee

router = APIRouter(prefix="/employees", tags=["Registration"])


@router.post("/register")
async def register_employee(
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    city: str = Form(...),
    image: UploadFile = File(...)
):
    if age <= 0 or age > 120:
        raise HTTPException(status_code=400, detail="Invalid age value")

    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image"
        )

    try:
        embedding = get_face_embedding(img)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    created_at = datetime.now().isoformat()

    try:
        employee_id = add_employee(
            name=name,
            age=age,
            email=email,
            city=city,
            embedding=embedding,
            created_at=created_at
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while saving employee data: {str(e)}"
        )

    return {
        "success": True,
        "message": "Employee registered successfully",
        "employee_id": employee_id
    }