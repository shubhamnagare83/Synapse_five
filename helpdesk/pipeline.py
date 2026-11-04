from helpdesk.search import search
from helpdesk.answer import generate_grounded_answer
from helpdesk.sql import validate_and_run_sql

def ask(question: str) -> dict:
    """
    Core routing function that decides whether a question requires 
    document search (rules, refunds, tatkal) or database queries (timetables).
    """
    q_lower = question.lower()
    
    # Simple heuristic to route timetable queries to SQL
    timetable_keywords = ["train", "schedule", "station", "depart", "arrive", "route", "stop", "duration", "km"]
    is_timetable_query = any(kw in q_lower for kw in timetable_keywords) and not any(kw in q_lower for kw in ["refund", "cancel", "tatkal", "rule", "charge", "quota"])

    if is_timetable_query:
        try:
            # Generate or map SQL query for timetable questions
            # (In production, use Gemini with schema definition to generate the SQL string first)
            sql_query = f"SELECT * FROM stations WHERE name LIKE '%{question}%' LIMIT 5;" # Placeholder query
            results = validate_and_run_sql(sql_query)
            
            if isinstance(results, dict) and "error" in results:
                return {"answer": "I couldn't retrieve the timetable details safely.", "sources": [], "sql": sql_query, "dont_know": True}
                
            return {
                "answer": f"Found timetable records: {results}",
                "sources": [],
                "sql": sql_query,
                "dont_know": False
            }
        except Exception:
            return {"answer": "I don't know how to query that timetable request.", "sources": [], "sql": None, "dont_know": True}
    else:
        # Route to document search
        chunks = search(question, k=3)
        result = generate_grounded_answer(question, chunks)
        result["sql"] = None
        return result