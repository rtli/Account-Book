"""
Migration script: Import old CSV data into the new SQLite database.
Usage: python -m backend.migrate
"""

import csv
import os
import sys
from datetime import date, datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.models import Category, Spending
from backend import constants as C

OLD_SPENDING_FILE = C.OLD_SPENDING_FILE
OLD_CLASSIFIER_FILE = C.OLD_CLASSIFIER_FILE


def migrate():
    init_db()
    db = SessionLocal()

    try:
        # Step 1: Migrate categories from classifier.csv
        if not os.path.exists(OLD_CLASSIFIER_FILE):
            print(f"[SKIP] {OLD_CLASSIFIER_FILE} not found")
        else:
            print(f"[INFO] Migrating categories from {OLD_CLASSIFIER_FILE}...")
            first_categories = {}  # name -> Category obj
            second_categories = {}  # name -> Category obj

            with open(
                OLD_CLASSIFIER_FILE, "r", encoding=C.CSV_ENCODING, newline=""
            ) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 2:
                        continue
                    second_name = row[0].strip()
                    first_name = row[1].strip()

                    # If mapping to 总支出, this is a first-level category
                    if first_name == C.TOTAL_EXPENSE:
                        if second_name not in first_categories:
                            cat = Category(name=second_name, level=1, parent_id=None)
                            db.add(cat)
                            db.flush()
                            first_categories[second_name] = cat
                            print(f"  [+] First-level: {second_name}")
                    else:
                        # This is a second-level -> first-level mapping
                        # Ensure parent (first-level) exists
                        if first_name not in first_categories:
                            cat = Category(name=first_name, level=1, parent_id=None)
                            db.add(cat)
                            db.flush()
                            first_categories[first_name] = cat
                            print(f"  [+] First-level: {first_name}")

                        # Create second-level category
                        if second_name not in second_categories:
                            parent = first_categories[first_name]
                            cat = Category(
                                name=second_name, level=2, parent_id=parent.id
                            )
                            db.add(cat)
                            db.flush()
                            second_categories[second_name] = cat
                            print(f"  [+] Second-level: {second_name} -> {first_name}")

            db.commit()
            print(
                f"[OK] Categories: {len(first_categories)} first-level, {len(second_categories)} second-level"
            )

        # Step 2: Migrate spending data
        if not os.path.exists(OLD_SPENDING_FILE):
            print(f"[SKIP] {OLD_SPENDING_FILE} not found")
        else:
            print(f"[INFO] Migrating spendings from {OLD_SPENDING_FILE}...")
            # Reload categories from DB for mapping
            all_categories = db.query(Category).filter(Category.level == 2).all()
            cat_map = {c.name: c.id for c in all_categories}

            imported = 0
            skipped = 0

            with open(OLD_SPENDING_FILE, "r", encoding=C.CSV_ENCODING, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 3:
                        skipped += 1
                        continue

                    item_name = row[0].strip()
                    category_name = row[1].strip()
                    try:
                        amount = float(row[2].strip())
                    except ValueError:
                        skipped += 1
                        continue

                    # Try to parse date from item_name (format: "M.D-name")
                    spend_date = date.today()
                    if "-" in item_name:
                        date_part = item_name.split("-", 1)[0]
                        try:
                            parts = date_part.split(".")
                            if len(parts) == 2:
                                month = int(parts[0])
                                day = int(parts[1])
                                spend_date = date(datetime.now().year, month, day)
                        except (ValueError, IndexError):
                            pass

                    category_id = cat_map.get(category_name)
                    if not category_id:
                        print(
                            f"  [!] Unknown category '{category_name}' for '{item_name}', skipping"
                        )
                        skipped += 1
                        continue

                    spending = Spending(
                        item_name=item_name,
                        category_id=category_id,
                        amount=amount,
                        spend_date=spend_date,
                    )
                    db.add(spending)
                    imported += 1

            db.commit()
            print(f"[OK] Spendings: {imported} imported, {skipped} skipped")

        print("\n[DONE] Migration complete!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
