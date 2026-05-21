from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.exceptions import CategoryNotFoundError, SpendingNotFoundError
from backend.models import Category, Spending
from backend.schemas import (
    SpendingCreate,
    SpendingListResponse,
    SpendingResponse,
    SpendingUpdate,
)

router = APIRouter(prefix="/api/spending", tags=["spending"])


def _to_response(s: Spending) -> SpendingResponse:
    return SpendingResponse(
        id=s.id,
        item_name=s.item_name,
        category_id=s.category_id,
        category_name=s.category.name if s.category else "",
        amount=s.amount,
        spend_date=s.spend_date,
        created_at=s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "",
    )


@router.get("", response_model=SpendingListResponse)
def list_spendings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Spending)

    if keyword:
        query = query.filter(Spending.item_name.contains(keyword))
    if category_id:
        query = query.filter(Spending.category_id == category_id)
    if start_date:
        query = query.filter(Spending.spend_date >= start_date)
    if end_date:
        query = query.filter(Spending.spend_date <= end_date)

    total = query.count()
    items = (
        query.order_by(Spending.spend_date.desc(), Spending.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return SpendingListResponse(
        items=[_to_response(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=SpendingResponse, status_code=201)
def create_spending(data: SpendingCreate, db: Session = Depends(get_db)):
    # Verify category exists
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise CategoryNotFoundError()

    spending = Spending(
        item_name=data.item_name,
        category_id=data.category_id,
        amount=data.amount,
        spend_date=data.spend_date or date.today(),
    )
    db.add(spending)
    db.commit()
    db.refresh(spending)
    return _to_response(spending)


@router.put("/{spending_id}", response_model=SpendingResponse)
def update_spending(
    spending_id: int, data: SpendingUpdate, db: Session = Depends(get_db)
):
    spending = db.query(Spending).filter(Spending.id == spending_id).first()
    if not spending:
        raise SpendingNotFoundError()

    if data.item_name is not None:
        spending.item_name = data.item_name
    if data.category_id is not None:
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise CategoryNotFoundError()
        spending.category_id = data.category_id
    if data.amount is not None:
        spending.amount = data.amount
    if data.spend_date is not None:
        spending.spend_date = data.spend_date

    db.commit()
    db.refresh(spending)
    return _to_response(spending)


@router.delete("/{spending_id}", status_code=204)
def delete_spending(spending_id: int, db: Session = Depends(get_db)):
    spending = db.query(Spending).filter(Spending.id == spending_id).first()
    if not spending:
        raise SpendingNotFoundError()
    db.delete(spending)
    db.commit()
