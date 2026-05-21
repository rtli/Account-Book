from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import extract, func
from sqlalchemy.orm import Session, aliased

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

# Top N categories to show individually; rest grouped as "其他"
TOP_N_CATEGORIES = 10


@router.get("/sankey", response_model=SankeyResponse)
def get_sankey_data(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Generate Sankey diagram data: sub_category -> parent_category -> total.

    Uses SQL-level aggregation instead of loading all records into memory.
    Only 2 layers: second_category -> first_category -> 总支出.
    """
    ParentCategory = aliased(Category)

    query = (
        db.query(
            Category.name.label("sub_cat"),
            ParentCategory.name.label("parent_cat"),
            func.sum(Spending.amount).label("total"),
        )
        .join(Category, Spending.category_id == Category.id)
        .join(ParentCategory, Category.parent_id == ParentCategory.id)
    )

    if year is not None:
        query = query.filter(extract("year", Spending.spend_date) == year)
    if month is not None:
        query = query.filter(extract("month", Spending.spend_date) == month)

    results = query.group_by(Category.name, ParentCategory.name).all()

    if not results:
        return SankeyResponse(nodes=[], links=[])

    nodes_set: set[str] = set()
    links: list[SankeyLink] = []

    # Layer 1: sub_category -> parent_category
    parent_totals: dict[str, float] = {}
    for row in results:
        sub_cat, parent_cat, total = row.sub_cat, row.parent_cat, row.total
        nodes_set.add(sub_cat)
        nodes_set.add(parent_cat)
        links.append(
            SankeyLink(source=sub_cat, target=parent_cat, value=round(total, 2))
        )
        parent_totals[parent_cat] = parent_totals.get(parent_cat, 0) + total

    # Layer 2: parent_category -> 总支出
    if parent_totals:
        nodes_set.add(C.TOTAL_EXPENSE)
        for cat_name, value in parent_totals.items():
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

    if year is not None:
        query = query.filter(extract("year", Spending.spend_date) == year)
    results = query.group_by("month").order_by("month").all()

    return [MonthlySummary(month=r.month, total=round(r.total, 2)) for r in results]


@router.get("/category-summary", response_model=list[CategorySummary])
def get_category_summary(
    year: Optional[int] = None,
    month: Optional[int] = None,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get spending totals grouped by category.

    By default aggregates at first-level (parent) categories.
    If parent_id is provided, shows sub-categories under that parent.
    Results beyond TOP_N are grouped into "其他".
    """
    if parent_id:
        # Drill-down: show sub-categories under a specific parent
        query = db.query(
            Category.name,
            func.sum(Spending.amount).label("total"),
        ).join(Category, Spending.category_id == Category.id).filter(
            Category.parent_id == parent_id
        )
        group_col = Category.name
    else:
        # Default: aggregate at first-level (parent) categories
        ParentCategory = aliased(Category)
        query = (
            db.query(
                ParentCategory.name,
                func.sum(Spending.amount).label("total"),
            )
            .join(Category, Spending.category_id == Category.id)
            .join(ParentCategory, Category.parent_id == ParentCategory.id)
        )
        group_col = ParentCategory.name

    if year is not None:
        query = query.filter(extract("year", Spending.spend_date) == year)
    if month is not None:
        query = query.filter(extract("month", Spending.spend_date) == month)

    results = (
        query.group_by(group_col)
        .order_by(func.sum(Spending.amount).desc())
        .all()
    )

    # Apply Top N grouping
    summaries: list[CategorySummary] = []
    other_total = 0.0

    for i, r in enumerate(results):
        if i < TOP_N_CATEGORIES:
            summaries.append(CategorySummary(name=r.name, total=round(r.total, 2)))
        else:
            other_total += r.total

    if other_total > 0:
        summaries.append(CategorySummary(name="其他", total=round(other_total, 2)))

    return summaries
