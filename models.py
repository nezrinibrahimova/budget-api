from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String

from database import Base


def current_time():
    return datetime.now(timezone.utc)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(String(7), nullable=False)
    category = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=current_time,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_amount"),
        CheckConstraint("type IN ('income', 'expense')", name="valid_type"),
    )
