import csv
import io

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend import constants as C
from backend.database import get_db
from backend.exceptions import (
    CSVFileRequiredError,
    CategoryDuplicateError,
    CategoryHasChildrenError,
    CategoryHasSpendingsError,
    CategoryNotFoundError,
    ParentCategoryNotFoundError,
)
from backend.models import Category, Spending
from backend.schemas import CategoryCreate, CategoryResponse, CategoryTree

router = APIRouter(prefix="/api/category", tags=["category"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.level, Category.id).all()
    return categories


@router.get("/tree", response_model=list[CategoryTree])
def get_category_tree(db: Session = Depends(get_db)):
    """Get categories as a tree structure (first-level with their children)."""
    first_level = (
        db.query(Category).filter(Category.level == 1).order_by(Category.id).all()
    )

    tree = []
    for parent in first_level:
        children = (
            db.query(Category)
            .filter(Category.parent_id == parent.id)
            .order_by(Category.id)
            .all()
        )
        tree.append(
            CategoryTree(
                id=parent.id,
                name=parent.name,
                level=parent.level,
                children=[
                    CategoryTree(id=c.id, name=c.name, level=c.level, children=[])
                    for c in children
                ],
            )
        )
    return tree


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    # Check duplicate name under same parent
    existing = (
        db.query(Category)
        .filter(Category.name == data.name, Category.parent_id == data.parent_id)
        .first()
    )
    if existing:
        raise CategoryDuplicateError()

    # For level 2, verify parent exists
    if data.level == 2 and data.parent_id:
        parent = db.query(Category).filter(Category.id == data.parent_id).first()
        if not parent:
            raise ParentCategoryNotFoundError()

    category = Category(name=data.name, parent_id=data.parent_id, level=data.level)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise CategoryNotFoundError()

    # Check if there are spendings using this category
    spending_count = (
        db.query(Spending).filter(Spending.category_id == category_id).count()
    )
    if spending_count > 0:
        raise CategoryHasSpendingsError()

    # Check if there are child categories
    children_count = (
        db.query(Category).filter(Category.parent_id == category_id).count()
    )
    if children_count > 0:
        raise CategoryHasChildrenError()

    db.delete(category)
    db.commit()


@router.post("/import")
async def import_categories(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Batch import categories from a CSV file.
    Expected format: second_category_name, first_category_name
    If the first-level category doesn't exist, it will be created automatically.
    """
    if not file.filename.endswith(C.CSV_EXTENSION):
        raise CSVFileRequiredError()

    content = await file.read()
    text = content.decode(C.CSV_ENCODING)
    reader = csv.reader(io.StringIO(text))

    imported = 0
    errors = []

    for i, row in enumerate(reader, 1):
        if len(row) < 2:
            errors.append(C.ERR_ROW_CATEGORY_COLS.format(row=i))
            continue

        second_name = row[0].strip()
        first_name = row[1].strip()

        if not second_name or not first_name:
            errors.append(C.ERR_ROW_EMPTY_NAME.format(row=i))
            continue

        # Find or create first-level category
        first_cat = (
            db.query(Category)
            .filter(Category.name == first_name, Category.level == 1)
            .first()
        )
        if not first_cat:
            first_cat = Category(name=first_name, level=1, parent_id=None)
            db.add(first_cat)
            db.flush()

        # Check if second-level already exists under this parent
        existing = (
            db.query(Category)
            .filter(
                Category.name == second_name,
                Category.parent_id == first_cat.id,
            )
            .first()
        )
        if existing:
            errors.append(
                C.ERR_ROW_CATEGORY_DUPLICATE.format(
                    row=i, second=second_name, first=first_name
                )
            )
            continue

        second_cat = Category(name=second_name, level=2, parent_id=first_cat.id)
        db.add(second_cat)
        imported += 1

    db.commit()
    return {"imported": imported, "errors": errors}
