import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException

from Db import get_connection
from model import get_face_embedding, compare_faces

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login-face")
async def login_face(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    try:
        embedding = get_face_embedding(img)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT employee_id, name, age, email, city, face_embedding, created_at FROM employees"
        )
        employees = cursor.fetchall()

        best_match = None
        best_similarity = -1.0

        for emp in employees:
            if not emp["face_embedding"]:
                continue

            stored_embedding = np.frombuffer(
                emp["face_embedding"], dtype=np.float32
            ).flatten()

            similarity, _ = compare_faces(embedding, stored_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = emp

        if best_match is None or best_similarity < 0.5:
            return {
                "success": False,
                "message": "Face not recognized",
                "employee": None,
                "similarity": float(best_similarity) if best_similarity != -1.0 else 0.0
            }

        return {
            "success": True,
            "message": "Login successful",
            "employee": {
                "employee_id": best_match["employee_id"],
                "name": best_match["name"],
                "age": best_match["age"],
                "email": best_match["email"],
                "city": best_match["city"],
                "created_at": best_match["created_at"]
            },
            "similarity": float(best_similarity)
        }
    finally:
        connection.close()