import sqlite3
import os
import re
from pathlib import Path

# Automatically detect database path whether running from project root or Synapse_five
BASE_DIR = Path(__file__).resolve().parent

CANDIDATE_DB_PATHS = [
    BASE_DIR / "database" / "rail_timetable.db",
    BASE_DIR.parent / "database" / "rail_timetable.db",
    Path("helpdesk/database/rail_timetable.db"),
    Path("database/rail_timetable.db")
]

def get_db_path() -> str:
    for p in CANDIDATE_DB_PATHS:
        if p.exists():
            return str(p.resolve())
    return str((BASE_DIR / "database" / "rail_timetable.db").resolve())


def is_safe_readonly_sql(query: str) -> bool:
    """
    Validates that the SQL query is strictly a read-only SELECT statement.
    Rejects any destructive or modifying statements.
    """
    if not query or not isinstance(query, str):
        return False
        
    cleaned = query.strip()
    # Remove leading comments if any
    cleaned = re.sub(r'^(?:--.*?\n|\/\*.*?\*\/)+', '', cleaned, flags=re.MULTILINE | re.DOTALL).strip()
    
    # Must start with SELECT or WITH (for CTEs)
    if not re.match(r'^(SELECT|WITH)\b', cleaned, re.IGNORECASE):
        return False
        
    # Check for forbidden modification keywords
    forbidden = [
        r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', r'\bALTER\b',
        r'\bCREATE\b', r'\bREPLACE\b', r'\bTRUNCATE\b', r'\bEXEC\b', r'\bPRAGMA\b',
        r'\bATTACH\b', r'\bDETACH\b'
    ]
    for pattern in forbidden:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False
            
    return True


def validate_and_run_sql(query: str):
    """
    Runs a strictly read-only SQL query against the SQLite timetable database.
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return {"error": f"Database file not found at {db_path}"}

    if not is_safe_readonly_sql(query):
        return {"error": "Security check failed: Only read-only SELECT statements are permitted."}

    # Connect using strict read-only URI mode
    db_uri = f"file:{db_path}?mode=ro"
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
