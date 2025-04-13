import os
import mimetypes
from time import time as current_time

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

    with conn.cursor() as curr:
        curr.execute("DELETE FROM files")

        file_data = []
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_path)
                name = os.path.basename(full_path)
                extension = os.path.splitext(full_path)[1].lower()

                content = read_text_file(full_path) if is_text_file(full_path) else None
                score = calculate_file_score({
                    'path': full_path,
                    'extension': extension
                })

                file_data.append((
                    rel_path,
                    name,
                    extension,
                    content,
                    content if content else "",
                    score
                ))

        insert_query = """
            INSERT INTO files (path, name, extension, content, content_tsvector, score)
            VALUES (%s, %s, %s, %s, to_tsvector('english', %s), %s)
        """

        curr.executemany(insert_query, file_data)
        conn.commit()

    conn.close()
    print("Indexing complete.")

def calculate_file_score(file_data):
    score = 0
    path = file_data['path']
    extension = file_data['extension']

    score -= len(path)

    if "writing" in path:
        score += 3

    prioritized_extensions = [".txt", ".docx"]
    if extension in prioritized_extensions:
        score += 5

    try:
        access_time = os.path.getatime(path)
        if current_time() - access_time < 3600 * 24:
            score += 3
    except:
        pass

    try:
        file_size = os.path.getsize(path)
        score -= file_size / 1000
    except:
        pass

    return score


def find_matching_files(self, parsed_query):
    query = "SELECT * FROM files WHERE "
    conditions = []

    if 'path' in parsed_query:
        path_conditions = " OR ".join([f"path LIKE '%{term}%'" for term in parsed_query['path']])
        conditions.append(f"({path_conditions})")

    if 'content' in parsed_query:
        content_conditions = " OR ".join([f"content LIKE '%{term}%'" for term in parsed_query['content']])
        conditions.append(f"({content_conditions})")

    query += " AND ".join(conditions)

    with self.db_cursor() as curr:
        curr.execute(query)
        return curr.fetchall()

def db_cursor(self):
    conn = connect_to_db(**self.db_params)
    return conn.cursor() if conn else None
