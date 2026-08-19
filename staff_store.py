import csv
import os

from config import STAFF_DB_FILE


class StaffRecordStore:
    """Persists staff records to a CSV file.

    The in-memory Hospital model is the single source of truth; save_all()
    rewrites the whole file from that model after every add/update/delete,
    so edits and deletes are reflected correctly (not just appends).
    """

    FIELDNAMES = ["name", "age", "position", "department"]

    def __init__(self, filepath: str = STAFF_DB_FILE):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self.save_all([])

    def load(self) -> list[dict]:
        """Return all stored staff records as a list of dicts."""
        with open(self.filepath, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def save_all(self, rows: list[dict]) -> None:
        """Rewrite the CSV file from the given list of row dicts."""
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
