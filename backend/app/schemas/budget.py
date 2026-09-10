from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.expense import CategoryStat, MonthlyStat


class BudgetBase(BaseModel):
    month: date
    category: str | None = Field(default=None, min_length=1, max_length=50)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    @field_validator("month")
    @classmethod
    def require_first_day_of_month(cls, value: date) -> date:
        if value.day != 1:
            raise ValueError("month must be the first day of a month")
        return value


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    total_spending: Decimal
    monthly_spending: Decimal
    budget: Decimal
    remaining_budget: Decimal
    top_category: str | None
    category_breakdown: list[CategoryStat]
    monthly_breakdown: list[MonthlyStat]
