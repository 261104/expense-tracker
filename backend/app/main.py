from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.routers import auth, dashboard, expenses

app = FastAPI(title="Expense Tracker API")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {"message": "Expense Tracker API"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
def database_health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "database": "reachable"}
