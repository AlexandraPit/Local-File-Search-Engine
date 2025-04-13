from db_utils import connect_to_db

def search_files(parsed_query, **db):
    conn = connect_to_db(**db)
    if not conn:
        return []

    conditions = []
    params = []

    if 'path' in parsed_query:
        path_conditions = []
        for term in parsed_query['path']:
            # Normalize slashes
            normalized = term.replace("\\", "/")

            # Remove drive prefix if necessary
            if normalized.lower().startswith("d:/scoala/"):
                normalized = normalized[len("d:/scoala/"):]

            path_conditions.append("path ILIKE %s")
            params.append(f"%{normalized}%")

        conditions.append("(" + " AND ".join(path_conditions) + ")")

    if 'content' in parsed_query:
        content_conditions = []
        for term in parsed_query['content']:
            content_conditions.append("to_tsvector('english', content) @@ plainto_tsquery('english', %s)")
            params.append(term)
        conditions.append("(" + " AND ".join(content_conditions) + ")")

    if 'general' in parsed_query:
        general_conditions = []
        for term in parsed_query['general']:
            general_conditions.append("(name ILIKE %s OR to_tsvector('english', content) @@ plainto_tsquery('english', %s))")
            params.extend([f"%{term}%", term])
        conditions.append("(" + " AND ".join(general_conditions) + ")")

    query = "SELECT path, name, extension FROM files"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY score DESC"

    with conn.cursor() as cur:
        cur.execute(query, params)
        results = cur.fetchall()

    conn.close()
    return results
