import csv
import io
from datetime import date

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
    Expected format: item_name, category_name, amount, date(optional: YYYY-MM-DD)
    """
    if not file.filename.endswith(C.CSV_EXTENSION):
        raise CSVFileRequiredError()

    content = await file.read()
    text = content.decode(C.CSV_ENCODING)
    reader = csv.reader(io.StringIO(text))

    imported = 0
    errors = []

    for i, row in enumerate(reader, 1):
        if len(row) < 3:
            errors.append(C.ERR_ROW_INSUFFICIENT_COLS.format(row=i))
            continue

        item_name = row[0].strip()
        category_name = row[1].strip()
        try:
            amount = float(row[2].strip())
        except ValueError:
            errors.append(C.ERR_ROW_AMOUNT_INVALID.format(row=i))
            continue

        spend_date = date.today()
        if len(row) >= 4 and row[3].strip():
            try:
                spend_date = date.fromisoformat(row[3].strip())
            except ValueError:
                errors.append(C.ERR_ROW_DATE_INVALID.format(row=i))

        # Find or skip category
        category = db.query(Category).filter(Category.name == category_name).first()
        if not category:
            errors.append(C.ERR_ROW_CATEGORY_MISSING.format(row=i, name=category_name))
            continue

        spending = Spending(
            item_name=item_name,
            category_id=category.id,
            amount=amount,
            spend_date=spend_date,
        )
        db.add(spending)
        imported += 1

    db.commit()
    return {"imported": imported, "errors": errors}


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
        writer.writerow(
            [
                s.item_name,
                s.category.name if s.category else "",
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
