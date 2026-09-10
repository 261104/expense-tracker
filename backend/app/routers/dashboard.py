from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies import get_current_user
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate, DashboardResponse
from app.services.dashboard import dashboard_data

router = APIRouter(tags=["budgets", "dashboard"])


@router.get("/budgets", response_model=list[BudgetResponse])
def get_budgets(month: Optional[date] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Budget).where(Budget.user_id == current_user.id)
    if month is not None:
        statement = statement.where(Budget.month == month)
    return db.scalars(statement.order_by(Budget.month.desc(), Budget.category)).all()


@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(budget_data: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    duplicate = db.scalar(select(Budget).where(Budget.user_id == current_user.id, Budget.month == budget_data.month, Budget.category == budget_data.category))
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="Budget already exists")
    budget = Budget(**budget_data.model_dump(), user_id=current_user.id)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.put("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, budget_data: BudgetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id))
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    for field, value in budget_data.model_dump().items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id))
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dashboard_data(db, current_user)
