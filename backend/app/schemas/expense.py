from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    payment_method: str | None = Field(default=None, max_length=30)
    date: date


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ExpensePage(BaseModel):
    items: list[ExpenseResponse]
    page: int
    limit: int
    total: int
    pages: int


class CategoryStat(BaseModel):
    category: str
    total: Decimal


class MonthlyStat(BaseModel):
    year: int
    month: int
    total: Decimal


class ExpenseStats(BaseModel):
    total_spending: Decimal
    average_expense: Decimal | None
    highest_expense: Decimal | None
    lowest_expense: Decimal | None
    category_breakdown: list[CategoryStat]
    monthly_breakdown: list[MonthlyStat]
