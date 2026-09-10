from datetime import date
from decimal import Decimal
from typing import Literal

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.user import User


def money_value(value: Decimal | float | int | None) -> Decimal | None:
    return Decimal(str(value)).quantize(Decimal("0.01")) if value is not None else None


def expense_filters(
    user: User,
    category: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        raise ValueError("min_amount cannot exceed max_amount")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("start_date cannot exceed end_date")
    filters = [Expense.user_id == user.id]
    if category:
        filters.append(Expense.category.ilike(category))
    if min_amount is not None:
        filters.append(Expense.amount >= min_amount)
    if max_amount is not None:
        filters.append(Expense.amount <= max_amount)
    if start_date is not None:
        filters.append(Expense.date >= start_date)
    if end_date is not None:
        filters.append(Expense.date <= end_date)
    return filters


def list_expenses(db: Session, user: User, *, category: str | None, min_amount: Decimal | None,
                  max_amount: Decimal | None, start_date: date | None, end_date: date | None,
                  sort_by: Literal["date", "amount", "category", "id"], order: Literal["asc", "desc"],
                  page: int, limit: int):
    filters = expense_filters(user, category, min_amount, max_amount, start_date, end_date)
    sort_columns = {"date": Expense.date, "amount": Expense.amount, "category": Expense.category, "id": Expense.id}
    sort_column = sort_columns[sort_by]
    ordering = sort_column.asc() if order == "asc" else sort_column.desc()
    statement = select(Expense).where(*filters).order_by(ordering, Expense.id.desc()).offset((page - 1) * limit).limit(limit)
    total = db.scalar(select(func.count()).select_from(Expense).where(*filters)) or 0
    items = db.scalars(statement).all()
    return items, total


def expense_stats(db: Session, user: User):
    user_filter = Expense.user_id == user.id
    summary = db.execute(select(func.coalesce(func.sum(Expense.amount), 0), func.avg(Expense.amount), func.max(Expense.amount), func.min(Expense.amount)).where(user_filter)).one()
    category_rows = db.execute(select(Expense.category, func.sum(Expense.amount)).where(user_filter).group_by(Expense.category).order_by(func.sum(Expense.amount).desc())).all()
    monthly_rows = db.execute(select(extract("year", Expense.date), extract("month", Expense.date), func.sum(Expense.amount)).where(user_filter).group_by(extract("year", Expense.date), extract("month", Expense.date)).order_by(extract("year", Expense.date), extract("month", Expense.date))).all()
    return {
        "total_spending": money_value(summary[0]),
        "average_expense": money_value(summary[1]),
        "highest_expense": money_value(summary[2]),
        "lowest_expense": money_value(summary[3]),
        "category_breakdown": [{"category": category, "total": money_value(total)} for category, total in category_rows],
        "monthly_breakdown": [{"year": int(year), "month": int(month), "total": money_value(total)} for year, month, total in monthly_rows],
    }
