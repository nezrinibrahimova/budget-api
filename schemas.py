from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


def current_time():
    return datetime.now(timezone.utc)


class TransactionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: Literal["income", "expense"]
    category: str = Field(min_length=1, max_length=100)
    created_at: AwareDatetime = Field(
        default_factory=current_time,
        description="İstəyə bağlıdır. Yazılmasa indiki vaxt seçilir. Saat qurşağı göstərilməlidir.",
    )

    @field_validator("amount", mode="before")
    @classmethod
    def check_amount_type(cls, value):
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise ValueError("Məbləğ rəqəm olmalıdır, məsələn: 25.50")
        return value


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    type: Literal["income", "expense"]
    category: str
    created_at: datetime


class BudgetSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
