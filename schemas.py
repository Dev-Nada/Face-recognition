from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmployeeCreate(BaseModel):
    name: str
    age: int
    email: EmailStr     
    city: str



class EmployeeOut(BaseModel):
    employee_id: int
    name: str
    age: int
    email: EmailStr
    city: str
    created_at: str
    class Config:

        from_attributes = True



class FaceLoginResponse(BaseModel):
    success: bool
    message: str
    employee: Optional[EmployeeOut] = None   
    similarity: Optional[float] = None


class MessageResponse(BaseModel):
    success: bool
    message: str



class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    check_in: str
    check_out: Optional[str] = None

    class Config:
        from_attributes = True