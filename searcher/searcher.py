from database.db_utils import connect_to_db
from searcher.query_builder import build_search_query

def fetch_and_format_results(parsed_query, **db):
    conn = connect_to_db(**db)
    if not conn:
        return []

    query, params = build_search_query(parsed_query)

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

        formatted = [{
            "path": row[0],
            "name": row[1],
            "extension": row[2],
            "modified_time": row[3],
        } for row in rows]

    conn.close()
    return formatted


def infer_language(extension):
    ext_to_lang = {
        ".py": "Python", ".java": "Java", ".c": "C", ".cpp": "C++",
        ".js": "JavaScript", ".html": "HTML", ".css": "CSS",
        ".sql": "SQL", ".rb": "Ruby"
    }
    return ext_to_lang.get(extension.lower(), "Unknown")