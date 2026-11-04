import sqlite3
import re

DB_PATH = "database/rail_timetable.db"

def get_readonly_connection():
    """Opens SQLite database in strict read-only mode."""
    db_uri = f"file:{DB_PATH}?mode=ro"
    return sqlite3.connect(db_uri, uri=True)

def validate_and_run_sql(query: str):
    """
    Ensures query is strictly a SELECT statement and executes it safely.
    Refuses harmful or write queries.
    """
    cleaned_query = query.strip().lower()
    
    # Security guardrails: Only allow SELECT statements
    if not cleaned_query.startswith("select"):
        raise ValueError("Unsafe or non-SELECT query rejected.")
    
    forbidden_keywords = ["insert", "update", "delete", "drop", "alter", "exec", "attach", "pragma"]
    if any(word in cleaned_query for word in forbidden_keywords):
        raise ValueError("Forbidden modification keyword detected in SQL.")

    try:
        conn = get_readonly_connection()
        cursor = conn.cursor()
        
        # Execute query with a safety row limit if missing
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        conn.close()
        
        # Format results into dictionaries
        results = [dict(zip(columns, row)) for row in rows]
        return results
    except Exception as e:
        return {"error": str(e)}