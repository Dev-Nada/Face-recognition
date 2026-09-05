from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dataForm import tables
from emplyees import router as employees_router
from routers import attendance, auth, reg


tables()

app = FastAPI(title="Face Recognition Attendance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reg.router)
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(employees_router)


@app.get("/")
def home():
    return {"message": "Face Recognition Attendance API is running"}
