import os
import mimetypes
from datetime import time

from db_utils import connect_to_db

def is_text_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type is not None and mime_type.startswith("text")

def read_text_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()
    except Exception:
        return None

def crawl_and_index(root_path, **db):
    conn = connect_to_db(**db)
    if not conn:
        print("Failed to connect to database.")
        return

    with conn.cursor() as cur:
        # Clear previous records
        cur.execute("DELETE FROM files")

        file_data = []
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_path)
                name = os.path.basename(full_path)
                extension = os.path.splitext(full_path)[1].lower()

                # Read content only for text files, else set to None
                content = read_text_file(full_path) if is_text_file(full_path) else None

                # Use empty string for content_tsvector if no content, otherwise pass the content
                file_data.append((
                    rel_path,
                    name,
                    extension,
                    content,
                    content if content else ""
                ))

        insert_query = """
            INSERT INTO files (path, name, extension, content, content_tsvector)
            VALUES (%s, %s, %s, %s, to_tsvector('english', %s))
        """
        cur.executemany(insert_query, file_data)
        conn.commit()

    conn.close()
    print("Indexing complete.")

def calculate_file_score(self, file_data, query_terms):
    score = 0

    score -= len(file_data['path'])  # Longer paths lower the score

    if any(term in file_data['path'] for term in query_terms.get('path', [])):
        score += 2  # Increase score if path contains search query

    important_dirs = ["Documents", "Downloads"]
    if any(dir in file_data['path'] for dir in important_dirs):
        score += 3  # Increase score for important directories

    prioritized_extensions = [".txt", ".docx"]
    if file_data['extension'] in prioritized_extensions:
        score += 5  # Boost for certain extensions

    access_time = os.path.getatime(file_data['path'])
    recent_access = time.time() - access_time < 3600 * 24  # Last 24 hours
    if recent_access:
        score += 3  # Boost score if file was accessed recently

    file_size = os.path.getsize(file_data['path'])
    score -= file_size / 1000  # Penalize large files

    return score

def find_matching_files(self, parsed_query):
    query = "SELECT * FROM files WHERE "
    conditions = []

    # Check path query terms
    if 'path' in parsed_query:
        path_conditions = " OR ".join([f"path LIKE '%{term}%'" for term in parsed_query['path']])
        conditions.append(f"({path_conditions})")

    # Check content query terms
    if 'content' in parsed_query:
        content_conditions = " OR ".join([f"content LIKE '%{term}%'" for term in parsed_query['content']])
        conditions.append(f"({content_conditions})")

    query += " AND ".join(conditions)

    # Execute the query on the DB
    with self.db_cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def db_cursor(self):
    # Helper to get database connection and cursor
    conn = connect_to_db(**self.db_params)
    return conn.cursor() if conn else None
