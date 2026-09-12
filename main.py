from contextlib import asynccontextmanager
from datetime import datetime, time, timezone
from decimal import Decimal
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Transaction
from schemas import BudgetSummary, TransactionCreate, TransactionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError:
        engine.dispose()
        raise RuntimeError(
            "PostgreSQL-ə qoşulmaq olmadı. .env məlumatlarını və budget_db bazasını yoxlayın."
        ) from None
    yield
    engine.dispose()


app = FastAPI(title="Şəxsi Büdcə API", version="1.0.0", lifespan=lifespan)


@app.post("/transactions/", response_model=TransactionResponse, status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    transaction = Transaction(
        amount=data.amount,
        type=data.type,
        category=data.category,
        created_at=data.created_at,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def read_date(value: str | None, field_name: str):
    if value is None:
        return None

    try:
        result = datetime.strptime(value, "%Y-%m-%d").date()
        if result.isoformat() != value:
            raise ValueError
        return result
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: Tarixi YYYY-MM-DD formatında yazın. Məsələn: 2026-09-12. Tarix mövcud gün olmalıdır.",
        ) from None


@app.get("/transactions/", response_model=list[TransactionResponse])
def list_transactions(
    type: Literal["income", "expense"] | None = None,
    start_date: str | None = Query(None, description="YYYY-MM-DD, məsələn: 2026-09-12"),
    end_date: str | None = Query(None, description="YYYY-MM-DD, məsələn: 2026-09-12"),
    db: Session = Depends(get_db),
):
    start_date = read_date(start_date, "start_date")
    end_date = read_date(end_date, "end_date")

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Başlanğıc tarixi bitiş tarixindən sonra ola bilməz.",
        )

    query = select(Transaction)
    if type is not None:
        query = query.where(Transaction.type == type)
    if start_date is not None:
        start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        query = query.where(Transaction.created_at >= start)
    if end_date is not None:
        end = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        query = query.where(Transaction.created_at <= end)

    query = query.order_by(Transaction.created_at.desc(), Transaction.id.desc())
    return db.scalars(query).all()


@app.get("/budget/summary", response_model=BudgetSummary)
def budget_summary(db: Session = Depends(get_db)):
    transactions = db.scalars(select(Transaction)).all()
    income = Decimal("0.00")
    expense = Decimal("0.00")

    for transaction in transactions:
        if transaction.type == "income":
            income = income + transaction.amount
        else:
            expense = expense + transaction.amount

    return {
        "total_income": income,
        "total_expense": expense,
        "balance": income - expense,
    }
