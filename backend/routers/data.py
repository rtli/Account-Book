import csv
import io
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend import constants as C
from backend.database import get_db
from backend.exceptions import CSVFileRequiredError
from backend.models import Category, Spending

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/import")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import spending data from a CSV file.
    Expected format: item_name, first_category, second_category, amount, date(optional)
    Supported date formats: YYYY-MM-DD, YYYY/MM/DD, YYYY-MM-DD HH:MM:SS, YYYY/MM/DD HH:MM:SS
    If categories don't exist, they will be created automatically.
    """
    if not file.filename.endswith(C.CSV_EXTENSION):
        raise CSVFileRequiredError()

    content = await file.read()
    text = content.decode(C.CSV_ENCODING)
    reader = csv.reader(io.StringIO(text))

    imported = 0
    errors = []

    for i, row in enumerate(reader, 1):
        if len(row) < 4:
            errors.append(C.ERR_ROW_INSUFFICIENT_COLS.format(row=i))
            continue

        item_name = row[0].strip()
        first_name = row[1].strip()
        second_name = row[2].strip()

        if not first_name or not second_name:
            errors.append(C.ERR_ROW_EMPTY_NAME.format(row=i))
            continue

        try:
            amount = float(row[3].strip())
        except ValueError:
            errors.append(C.ERR_ROW_AMOUNT_INVALID.format(row=i))
            continue

        spend_date = date.today()
        if len(row) >= 5 and row[4].strip():
            raw_date = row[4].strip()
            parsed = False
            for fmt in C.CSV_DATE_FORMATS:
                try:
                    spend_date = datetime.strptime(raw_date, fmt).date()
                    parsed = True
                    break
                except ValueError:
                    continue
            if not parsed:
                errors.append(C.ERR_ROW_DATE_INVALID.format(row=i))

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

        # Find or create second-level category
        second_cat = (
            db.query(Category)
            .filter(Category.name == second_name, Category.parent_id == first_cat.id)
            .first()
        )
        if not second_cat:
            second_cat = Category(name=second_name, level=2, parent_id=first_cat.id)
            db.add(second_cat)
            db.flush()

        spending = Spending(
            item_name=item_name,
            category_id=second_cat.id,
            amount=amount,
            spend_date=spend_date,
        )
        db.add(spending)
        imported += 1

    db.commit()
    return {"imported": imported, "errors": errors}


@router.delete("/clear", status_code=200)
def clear_all_spendings(db: Session = Depends(get_db)):
    """Delete all spending records."""
    count = db.query(Spending).count()
    db.query(Spending).delete()
    db.commit()
    return {"deleted": count}


@router.get("/export")
def export_csv(db: Session = Depends(get_db)):
    """Export all spending data as CSV."""
    spendings = (
        db.query(Spending)
        .order_by(Spending.spend_date.desc(), Spending.id.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(C.EXPORT_HEADERS)

    for s in spendings:
        first_name = ""
        second_name = ""
        if s.category:
            if s.category.parent:
                first_name = s.category.parent.name
                second_name = s.category.name
            else:
                first_name = s.category.name
        writer.writerow(
            [
                s.item_name,
                first_name,
                second_name,
                s.amount,
                s.spend_date.isoformat(),
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={C.EXPORT_FILENAME}"},
    )
