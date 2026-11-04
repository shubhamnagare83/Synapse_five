import sqlite3
import os

DB_PATH = "database/rail_timetable.db"

def validate_and_run_sql(query: str):
    """
    Runs a read-only SQL query against the SQLite timetable database.
    """
    if not os.path.exists(DB_PATH):
        return {"error": f"Database file not found at {DB_PATH}"}
    
    # Enforce read-only URI connection mode
    db_uri = f"file:{os.path.abspath(DB_PATH)}?mode=ro"
    try:
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        return {"error": str(e)}