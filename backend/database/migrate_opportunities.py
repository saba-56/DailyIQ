
import sqlite3
from pathlib import Path

# Resolve the database relative to the backend folder,
# regardless of the terminal's current working directory.
DB_PATH = Path(__file__).resolve().parent.parent / "dailyiq.db"

NEW_COLUMNS = {
    "degree": "VARCHAR(100)",
    "branch": "VARCHAR(100)",
    "study_year": "VARCHAR(100)",
    "required_skills": "TEXT",
    "location": "VARCHAR(150)",
    "source_url": "VARCHAR(500)",
    "verified": "BOOLEAN NOT NULL DEFAULT 0",
}


def migrate():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. "
            "Start from your existing backend database location."
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(opportunities)")
        existing_columns = {
            row[1] for row in cursor.fetchall()
        }

        if not existing_columns:
            raise RuntimeError(
                "The opportunities table was not found. "
                "Check that this is the correct database."
            )

        for column_name, column_type in NEW_COLUMNS.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE opportunities "
                    f"ADD COLUMN {column_name} {column_type}"
                )
                print(f"Added column: {column_name}")
            else:
                print(f"Already exists: {column_name}")

        connection.commit()
        print("Opportunity database migration completed.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()