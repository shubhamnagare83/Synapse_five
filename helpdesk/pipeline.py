import re
from helpdesk.search import search
from helpdesk.answer import generate_grounded_answer
from helpdesk.sql import validate_and_run_sql
from helpdesk.llm import generate_content_with_retry

def format_timetable_answer(results: list) -> str:
    """Formats raw database rows into a clean, human-readable timetable summary."""
    if not results or not isinstance(results, list):
        return "No records found."
    
    if len(results) == 1:
        row = results[0]
        lines = []
        for k, v in row.items():
            clean_k = k.replace("_", " ").title()
            lines.append(f"• {clean_k}: {v}")
        return "\n".join(lines)
    
    # If list of stations / schedules
    first = results[0]
    if "station_code" in first or "station_name" in first:
        lines = ["Route Schedule:"]
        lines.append(f"{'Seq':<4} | {'Station':<25} | {'Arr':<6} | {'Dep':<6} | {'Halt':<6}")
        lines.append("-" * 55)
        for r in results:
            seq = r.get("stop_sequence", "")
            stn = r.get("station_name") or r.get("station_code") or ""
            arr = r.get("arrival") or "--"
            dep = r.get("departure") or "--"
            halt = f"{r.get('halt_min', 0)}m" if r.get("halt_min") is not None else "--"
            lines.append(f"{seq:<4} | {stn[:25]:<25} | {arr:<6} | {dep:<6} | {halt:<6}")
        return "\n".join(lines)
    
    # Generic table format for any multiple rows
    keys = list(first.keys())
    header = " | ".join([k.replace('_', ' ').title() for k in keys])
    separator = "-" * len(header)
    rows_text = [header, separator]
    for r in results[:15]:  # limit to top 15 rows for clarity
        rows_text.append(" | ".join([str(r.get(k, '')) for k in keys]))
    if len(results) > 15:
        rows_text.append(f"... and {len(results) - 15} more rows.")
    return "\n".join(rows_text)


def format_timetable_answer(results: list) -> str:
    """Formats raw database rows into a clean, human-readable timetable summary."""
    if not results or not isinstance(results, list):
        return "No records found."
    
    # If single record (e.g. train summary)
    if len(results) == 1:
        row = results[0]
        lines = []
        for k, v in row.items():
            clean_k = k.replace("_", " ").title()
            lines.append(f"• {clean_k}: {v}")
        return "\n".join(lines)
    
    # If list of stations / schedules
    first = results[0]
    if "station_code" in first or "station_name" in first:
        lines = ["Route Schedule:"]
        lines.append(f"{'Seq':<4} | {'Station':<25} | {'Arr':<6} | {'Dep':<6} | {'Halt':<6}")
        lines.append("-" * 55)
        for r in results:
            seq = r.get("stop_sequence", "")
            stn = r.get("station_name") or r.get("station_code") or ""
            arr = r.get("arrival") or "--"
            dep = r.get("departure") or "--"
            halt = f"{r.get('halt_min', 0)}m" if r.get("halt_min") is not None else "--"
            lines.append(f"{seq:<4} | {stn[:25]:<25} | {arr:<6} | {dep:<6} | {halt:<6}")
        return "\n".join(lines)
    
    # Generic table format for any multiple rows
    keys = list(first.keys())
    header = " | ".join([k.replace('_', ' ').title() for k in keys])
    separator = "-" * len(header)
    rows_text = [header, separator]
    for r in results[:15]:  # limit to top 15 rows for clarity
        rows_text.append(" | ".join([str(r.get(k, '')) for k in keys]))
    if len(results) > 15:
        rows_text.append(f"... and {len(results) - 15} more rows.")
    return "\n".join(rows_text)


def clean_sql_response(raw_text: str) -> str:
    """Extracts and sanitizes SQL query from LLM output."""
    if not raw_text:
        return ""
    # Strip markdown block formatting
    query = re.sub(r'```(?:sql)?', '', raw_text, flags=re.IGNORECASE).replace('```', '').strip()
    # Normalize multiple semicolons or trailing spaces
    query = query.rstrip(';') + ';'
    return query

def ask(question: str) -> dict:
    """
    Core routing function that decides whether a question requires 
    document search or database queries (timetables), returning structured output.
    """
    q_lower = question.lower()
    
    # Specific timetable & train operation intent keywords
    timetable_keywords = [
        "timing", "timings", "timetable", "time table", "schedule", "schedules", 
        "arrival time", "departure time", "route of", "stops of", "duration of", 
        "distance between", "train between", "trains from", "trains between", "halt time"
    ]
    # Document, rule, policy, booking, cancellation, refund keywords
    document_keywords = [
        "book", "booking", "refund", "cancellation", "cancel", "tatkal", "rule", "rules", 
        "charge", "charges", "clerkage", "quota", "advance reservation", "arp", "chart", 
        "charting", "current booking", "tdr", "concession", "pehle", "kar sakthe"
    ]
    
    # Question is routed to timetable SQL ONLY if it seeks timetable data and is NOT a policy/booking query
    is_timetable_query = (
        (any(kw in q_lower for kw in timetable_keywords) or re.search(r'\b\d{5}\b', q_lower))
        and not any(kw in q_lower for kw in document_keywords)
    )


    if is_timetable_query:
        sql_query = None
        try:
            sql_prompt = f"""You are an SQLite expert for an Indian Railways 2016 timetable database.
Given the exact schema:
- stations (code, name, state, zone, address, latitude, longitude)
- trains (number, name, type_code, zone, from_station_code, to_station_code, departure, arrival, duration_min, distance_km, return_train, has_1a, has_2a, has_3a, has_sl, has_cc, has_fc)
- schedules (train_number, stop_sequence, station_code, day, arrival, departure, halt_min, is_halt)
- stops view (SELECT * FROM schedules WHERE is_halt = 1)

CRITICAL RULES:
1. Return ONLY a single valid SQLite read-only query (SELECT statement). Do NOT explain or include markdown prose.
2. Train numbers in table 'trains' are stored as TEXT (e.g., '12951', '01101'). Always quote train numbers like train_number = '12951' or LIKE '%12951%'.
3. Station names are UPPERCASE or mixed case (e.g. use LIKE '%MUMBAI%').
4. For trains between two cities/stations (e.g., A to B), join 'stops' (or 'trains') with DISTINCT train_number, s_from.departure, s_to.arrival, and ensure s_from.stop_sequence < s_to.stop_sequence. Do NOT duplicate trains. Use LIMIT 15.
5. For train schedules, query the 'stops' view (e.g. SELECT stop_sequence, station_code, day, arrival, departure, halt_min FROM stops WHERE train_number = '12951' ORDER BY stop_sequence) so only actual halts are returned, or join with stations ON station_code = stations.code.

Question: {question}
Return ONLY the raw SQL query:"""

            res = generate_content_with_retry(sql_prompt, model='gemini-3.5-flash-lite')
            sql_query = clean_sql_response(res.text)

            if not sql_query.upper().startswith("SELECT") and not sql_query.upper().startswith("WITH"):
                # Safety fallback for train lookup
                train_num_match = re.search(r'\b\d{5}\b', question)
                if train_num_match:
                    sql_query = f"SELECT number, name, departure, arrival, distance_km, duration_min FROM trains WHERE number = '{train_num_match.group(0)}';"
                else:
                    sql_query = None

            if sql_query:
                results = validate_and_run_sql(sql_query)
                
                if isinstance(results, dict) and "error" in results:
                    return {
                        "answer": f"Could not execute timetable query: {results['error']}", 
                        "sources": [], 
                        "sql_query": sql_query, 
                        "dont_know": True
                    }
                
                if not results:
                    return {
                        "answer": f"No timetable records found in the database for query: {question}",
                        "sources": [],
                        "sql_query": sql_query,
                        "dont_know": False
                    }
                    
                clean_answer = format_timetable_answer(results)
                return {
                    "answer": clean_answer,
                    "sources": [],
                    "sql_query": sql_query,
                    "dont_know": False
                }
            else:
                return {
                    "answer": "I don't know how to query that timetable request.", 
                    "sources": [], 
                    "sql_query": None, 
                    "dont_know": True
                }
        except Exception as e:
            return {
                "answer": f"Error processing timetable query: {str(e)}", 
                "sources": [], 
                "sql_query": sql_query, 
                "dont_know": True
            }
    else:
        chunks = search(question, k=3)
        result = generate_grounded_answer(question, chunks)
        result["sql_query"] = None
        return result
