def build_search_query(parsed_query):
    conditions = []
    params = []

    if 'path' in parsed_query:
        path_conditions = []
        for term in parsed_query['path']:
            normalized = term.replace("\\", "/")
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

    query = "SELECT path, name, extension, modified_time FROM files"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY score DESC"

    return query, params
