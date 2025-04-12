from db_utils import connect_to_db

def search_files(query, **db):
    conn = connect_to_db(**db)
    if not conn:
        return []
    with conn.cursor() as cur:
        ts_query = " & ".join(query.split())
        cur.execute("""
            SELECT path, content FROM files
            WHERE content_tsvector @@ to_tsquery('english', %s)
               OR name ILIKE %s
        """, (ts_query, f"%{query}%"))
        return cur.fetchall()
