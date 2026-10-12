
import sqlite3
from pathlib import Path

# Use the same existing DailyIQ database.
DB_PATH = Path(__file__).resolve().parent.parent / "dailyiq.db"


def migrate():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}"
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(affairs)")
        existing_columns = {
            row[1] for row in cursor.fetchall()
        }

        if not existing_columns:
            raise RuntimeError(
                "The affairs table was not found. "
                "Check the database path."
            )

        if "published_at" not in existing_columns:
            cursor.execute(
                "ALTER TABLE affairs "
                "ADD COLUMN published_at VARCHAR(50)"
            )
            print("Added column: published_at")
        else:
            print("Column already exists: published_at")

        connection.commit()
        print("Affairs database migration completed.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()