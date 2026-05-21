from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Category, Spending
from backend import constants as C
from backend.schemas import (
    CategorySummary,
    MonthlySummary,
    SankeyLink,
    SankeyNode,
    SankeyResponse,
)

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/sankey", response_model=SankeyResponse)
def get_sankey_data(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Generate Sankey diagram data: item -> second_category -> first_category -> total."""
    query = db.query(Spending)

    if year:
        query = query.filter(extract("year", Spending.spend_date) == year)
    if month:
        query = query.filter(extract("month", Spending.spend_date) == month)

    spendings = query.all()
    if not spendings:
        return SankeyResponse(nodes=[], links=[])

    nodes_set = set()
    links = []

    # Layer 1: item -> second_category (level 2)
    item_to_cat = {}
    for s in spendings:
        cat = s.category
        if not cat:
            continue
        item_key = s.item_name
        nodes_set.add(item_key)
        nodes_set.add(cat.name)

        key = (item_key, cat.name)
        item_to_cat[key] = item_to_cat.get(key, 0) + s.amount

    for (source, target), value in item_to_cat.items():
        links.append(SankeyLink(source=source, target=target, value=round(value, 2)))

    # Layer 2: second_category -> first_category (level 1)
    cat2_to_cat1 = {}
    for s in spendings:
        cat = s.category
        if not cat or not cat.parent:
            continue
        parent = cat.parent
        nodes_set.add(parent.name)

        key = (cat.name, parent.name)
        cat2_to_cat1[key] = cat2_to_cat1.get(key, 0) + s.amount

    for (source, target), value in cat2_to_cat1.items():
        links.append(SankeyLink(source=source, target=target, value=round(value, 2)))

    # Layer 3: first_category -> 总支出
    cat1_totals = {}
    for s in spendings:
        cat = s.category
        if not cat or not cat.parent:
            continue
        parent = cat.parent
        cat1_totals[parent.name] = cat1_totals.get(parent.name, 0) + s.amount

    if cat1_totals:
        nodes_set.add(C.TOTAL_EXPENSE)
        for cat_name, value in cat1_totals.items():
            links.append(
                SankeyLink(
                    source=cat_name, target=C.TOTAL_EXPENSE, value=round(value, 2)
                )
            )

    nodes = [SankeyNode(name=n) for n in nodes_set]
    return SankeyResponse(nodes=nodes, links=links)


@router.get("/monthly", response_model=list[MonthlySummary])
def get_monthly_summary(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get monthly spending totals."""
    query = db.query(
        func.strftime(C.MONTH_FORMAT, Spending.spend_date).label("month"),
        func.sum(Spending.amount).label("total"),
    )

    if year:
        query = query.filter(extract("year", Spending.spend_date) == year)

    results = query.group_by("month").order_by("month").all()

    return [MonthlySummary(month=r.month, total=round(r.total, 2)) for r in results]


@router.get("/category-summary", response_model=list[CategorySummary])
def get_category_summary(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get spending totals grouped by category."""
    query = db.query(
        Category.name,
        func.sum(Spending.amount).label("total"),
    ).join(Category, Spending.category_id == Category.id)

    if year:
        query = query.filter(extract("year", Spending.spend_date) == year)
    if month:
        query = query.filter(extract("month", Spending.spend_date) == month)

    results = (
        query.group_by(Category.name).order_by(func.sum(Spending.amount).desc()).all()
    )

    return [CategorySummary(name=r.name, total=round(r.total, 2)) for r in results]
