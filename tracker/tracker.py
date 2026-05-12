"""
tracker/tracker.py

SQLite-based application tracker.
Tracks job applications, statuses, contacts, and follow-up dates.

Usage:
    from tracker.tracker import ApplicationTracker
    
    tracker = ApplicationTracker()
    
    # Add application
    tracker.add(
        company="Acme Corp",
        role="Advisory Consultant DS",
        status="interview",
        contact="Alex Johnson",
        notes="Round 1 done. Round 2 face to face pending."
    )
    
    # Get all applications
    apps = tracker.get_all()
    
    # Get applications needing follow-up
    stale = tracker.get_stale(days=14)
"""

import sqlite3
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

try:
    import config
    DB_PATH = config.TRACKER_DB_PATH
    NO_RESPONSE_DAYS = config.NO_RESPONSE_DAYS
except ImportError:
    DB_PATH = "tracker/applications.db"
    NO_RESPONSE_DAYS = 14


VALID_STATUSES = [
    "applied",
    "screening",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
    "no_response",
]


@dataclass
class Application:
    id: Optional[int]
    company: str
    role: str
    status: str
    applied_date: str
    last_contact: str
    contact_name: str = ""
    contact_email: str = ""
    notes: str = ""
    jd_url: str = ""
    salary_range: str = ""
    next_action: str = ""
    next_action_date: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ApplicationTracker:
    """
    SQLite-backed job application tracker.
    Tracks status, contacts, dates, and follow-up actions.
    """

    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    role TEXT,
                    status TEXT DEFAULT 'applied',
                    applied_date TEXT,
                    last_contact TEXT,
                    contact_name TEXT,
                    contact_email TEXT,
                    notes TEXT,
                    jd_url TEXT,
                    salary_range TEXT,
                    next_action TEXT,
                    next_action_date TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER,
                    event_type TEXT,
                    event_date TEXT,
                    notes TEXT,
                    FOREIGN KEY(application_id) REFERENCES applications(id)
                )
            """)

    def add(
        self,
        company: str,
        role: str = "",
        status: str = "applied",
        applied_date: str = "",
        contact_name: str = "",
        contact_email: str = "",
        notes: str = "",
        jd_url: str = "",
        salary_range: str = "",
        next_action: str = "",
        next_action_date: str = "",
    ) -> int:
        """Add a new application. Returns the new application ID."""
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Choose from: {VALID_STATUSES}")

        today = datetime.now().strftime("%Y-%m-%d")

        with self._connect() as conn:
            cursor = conn.execute("""
                INSERT INTO applications
                (company, role, status, applied_date, last_contact,
                 contact_name, contact_email, notes, jd_url,
                 salary_range, next_action, next_action_date, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                company, role, status,
                applied_date or today,
                today,
                contact_name, contact_email, notes, jd_url,
                salary_range, next_action, next_action_date,
                datetime.now().isoformat()
            ))
            app_id = cursor.lastrowid

            # Log the initial event
            conn.execute("""
                INSERT INTO events (application_id, event_type, event_date, notes)
                VALUES (?, ?, ?, ?)
            """, (app_id, "applied", applied_date or today, notes))

        return app_id

    def update_status(self, app_id: int, status: str, notes: str = "") -> bool:
        """Update application status and log the event."""
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Choose from: {VALID_STATUSES}")

        today = datetime.now().strftime("%Y-%m-%d")

        with self._connect() as conn:
            conn.execute("""
                UPDATE applications
                SET status = ?, last_contact = ?
                WHERE id = ?
            """, (status, today, app_id))

            conn.execute("""
                INSERT INTO events (application_id, event_type, event_date, notes)
                VALUES (?, ?, ?, ?)
            """, (app_id, status, today, notes))

        return True

    def update_notes(self, app_id: int, notes: str) -> bool:
        """Update notes for an application."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE applications SET notes = ? WHERE id = ?",
                (notes, app_id)
            )
        return True

    def get_all(self, status_filter: Optional[str] = None) -> list[dict]:
        """Get all applications, optionally filtered by status."""
        with self._connect() as conn:
            if status_filter:
                rows = conn.execute(
                    "SELECT * FROM applications WHERE status = ? ORDER BY applied_date DESC",
                    (status_filter,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM applications ORDER BY applied_date DESC"
                ).fetchall()
        return [dict(row) for row in rows]

    def get_by_id(self, app_id: int) -> Optional[dict]:
        """Get a single application by ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM applications WHERE id = ?", (app_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_stale(self, days: int = NO_RESPONSE_DAYS) -> list[dict]:
        """
        Get applications with no contact in N days.
        These need a follow-up.
        """
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM applications
                WHERE last_contact < ?
                AND status NOT IN ('offer', 'rejected', 'withdrawn')
                ORDER BY last_contact ASC
            """, (cutoff,)).fetchall()
        return [dict(row) for row in rows]

    def get_stats(self) -> dict:
        """Get summary statistics."""
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            by_status = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM applications
                GROUP BY status
            """).fetchall()

        stats = {"total": total}
        for row in by_status:
            stats[row["status"]] = row["count"]

        stale = self.get_stale()
        stats["needs_followup"] = len(stale)

        return stats

    def delete(self, app_id: int) -> bool:
        """Delete an application and its events."""
        with self._connect() as conn:
            conn.execute("DELETE FROM events WHERE application_id = ?", (app_id,))
            conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        return True

    def get_events(self, app_id: int) -> list[dict]:
        """Get event history for an application."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM events
                WHERE application_id = ?
                ORDER BY event_date ASC
            """, (app_id,)).fetchall()
        return [dict(row) for row in rows]

    def print_summary(self):
        """Print a formatted summary to console."""
        stats = self.get_stats()
        apps = self.get_all()
        stale = self.get_stale()

        print(f"\n{'='*50}")
        print(f"  JOB SEARCH TRACKER SUMMARY")
        print(f"{'='*50}")
        print(f"  Total applications: {stats['total']}")
        for status in VALID_STATUSES:
            count = stats.get(status, 0)
            if count:
                print(f"  {status.capitalize()}: {count}")
        print(f"  Needs follow-up ({NO_RESPONSE_DAYS}+ days): {stats['needs_followup']}")

        if stale:
            print(f"\n  FOLLOW-UP NEEDED:")
            for app in stale:
                print(f"  - {app['company']} ({app['role']}) — last contact: {app['last_contact']}")

        print(f"{'='*50}\n")


if __name__ == "__main__":
    tracker = ApplicationTracker(db_path="tracker/test_applications.db")

    # Add sample applications
    id1 = tracker.add(
        company="Acme Corp",
        role="Senior AI Engineer",
        status="interview",
        contact_name="Alex Johnson",
        notes="Round 1 virtual done. Round 2 face to face pending."
    )

    id2 = tracker.add(
        company="Example University",
        role="AI Center Head",
        status="screening",
        notes="First round interview done. Strategic role. Distance concern."
    )

    id3 = tracker.add(
        company="Nokia",
        role="Senior AI Engineer",
        status="applied",
    )

    tracker.print_summary()

    # Clean up test db
    import os
    os.remove("tracker/test_applications.db")
