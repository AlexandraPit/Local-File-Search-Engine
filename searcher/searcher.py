from database.db_utils import connect_to_db
from searcher.query_builder import build_search_query

def search_files(parsed_query, **db):
    conn = connect_to_db(**db)
    if not conn:
        return []

    query, params = build_search_query(parsed_query)

    with conn.cursor() as cur:
        cur.execute(query, params)
        results = cur.fetchall()

    conn.close()
    return results
