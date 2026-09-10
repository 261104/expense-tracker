from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.expense import Expense
from app.models.user import User
from app.services.expenses import expense_stats, money_value


def dashboard_data(db: Session, user: User):
    today = date.today()
    month_start = today.replace(day=1)
    next_month = date(today.year + 1, 1, 1) if today.month == 12 else date(today.year, today.month + 1, 1)
    user_filter = Expense.user_id == user.id
    total = money_value(db.scalar(select(func.sum(Expense.amount)).where(user_filter))) or Decimal("0.00")
    monthly = money_value(db.scalar(select(func.sum(Expense.amount)).where(user_filter, Expense.date >= month_start, Expense.date < next_month))) or Decimal("0.00")
    budget = money_value(db.scalar(select(func.sum(Budget.amount)).where(Budget.user_id == user.id, Budget.month == month_start, Budget.category.is_(None)))) or Decimal("0.00")
    top_category = db.execute(select(Expense.category).where(user_filter).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).limit(1)).scalar()
    stats = expense_stats(db, user)
    return {"total_spending": total, "monthly_spending": monthly, "budget": budget, "remaining_budget": budget - monthly, "top_category": top_category, "category_breakdown": stats["category_breakdown"], "monthly_breakdown": stats["monthly_breakdown"]}
