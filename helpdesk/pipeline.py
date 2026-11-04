from helpdesk.search import search
from helpdesk.answer import generate_grounded_answer
from helpdesk.sql import validate_and_run_sql
from helpdesk.llm import get_gemini_client

def ask(question: str) -> dict:
    """
    Core routing function that decides whether a question requires 
    document search or database queries (timetables), returning structured output.
    """
    q_lower = question.lower()
    
    timetable_keywords = ["train", "schedule", "station", "depart", "arrive", "route", "stop", "duration", "km", "train number"]
    exclude_keywords = ["refund", "cancel", "tatkal", "rule", "charge", "quota", "advance reservation"]
    
    is_timetable_query = any(kw in q_lower for kw in timetable_keywords) and not any(kw in q_lower for kw in exclude_keywords)

    if is_timetable_query:
        try:
            client = get_gemini_client()
            sql_prompt = f"""You are an SQLite expert for an Indian Railways 2016 timetable database. 
Given the schema:
- stations (code, name, state, zone, lat, lon)
- trains (number, name, type, has_1a, has_2a, has_3a, has_cc, has_sl, has_fc)
- schedules (train_number, station_code, arrival, departure, distance, day, stop_sequence, is_halt, halt_min)

Write a valid SQLite read-only query to answer this question: {question}
Return ONLY the raw SQL query string inside plain text or a code block, nothing else."""

            res = client.models.generate_content(model='gemini-3.8-flash', contents=sql_prompt) # Update model name here too
            if not sql_query.upper().startswith("SELECT"):
                sql_query = f"SELECT * FROM stations WHERE name LIKE '%{question}%' LIMIT 5;"

            results = validate_and_run_sql(sql_query)
            
            if isinstance(results, dict) and "error" in results:
                return {
                    "answer": "I couldn't retrieve the timetable details safely.", 
                    "sources": [], 
                    "sql": sql_query, 
                    "dont_know": True
                }
                
            return {
                "answer": f"Here are the timetable results: {results}",
                "sources": [],
                "sql": sql_query,
                "dont_know": False
            }
        except Exception:
            return {
                "answer": "I don't know how to query that timetable request.", 
                "sources": [], 
                "sql": None, 
                "dont_know": True
            }
    else:
        chunks = search(question, k=3)
        result = generate_grounded_answer(question, chunks)
        result["sql"] = None
        return result