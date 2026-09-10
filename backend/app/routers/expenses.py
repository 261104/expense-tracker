from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies import get_current_user
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpensePage, ExpenseResponse, ExpenseStats, ExpenseUpdate
from app.services.expenses import expense_stats, list_expenses

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=ExpensePage)
def get_expenses(category: str | None = Query(default=None, min_length=1), min_amount: Decimal | None = Query(default=None, gt=0), max_amount: Decimal | None = Query(default=None, gt=0), start_date: date | None = None, end_date: date | None = None, sort_by: Literal["date", "amount", "category", "id"] = "date", order: Literal["asc", "desc"] = "desc", page: int = Query(default=1, ge=1), limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        items, total = list_expenses(db, current_user, category=category, min_amount=min_amount, max_amount=max_amount, start_date=start_date, end_date=end_date, sort_by=sort_by, order=order, page=page, limit=limit)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"items": items, "page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}


@router.get("/stats", response_model=ExpenseStats)
def get_expense_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return expense_stats(db, current_user)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.scalar(select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id))
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense_data: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = Expense(**expense_data.model_dump(), user_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense_data: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.scalar(select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id))
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in expense_data.model_dump().items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.scalar(select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id))
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
