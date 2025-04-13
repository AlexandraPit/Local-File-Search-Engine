import json
import os
import mimetypes
from time import time as current_time
from datetime import datetime
from search_logger import SearchLogger

import config
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
        errors=[]

        file_data = []
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_path)
                name = os.path.basename(full_path)
                extension = os.path.splitext(full_path)[1].lower()

                try:
                    content = read_text_file(full_path) if is_text_file(full_path) else None
                except Exception as e:
                    errors.append(f"Failed to read {full_path}: {e}")
                    content = None


                file_data.append((
                    rel_path,
                    name,
                    extension,
                    content,
                    content if content else "",

                ))

        insert_query = """
            INSERT INTO files (path, name, extension, content, content_tsvector)
                       VALUES (%s, %s, %s, %s, to_tsvector('english', %s))
        """

        curr.executemany(insert_query, file_data)
        conn.commit()

    conn.close()
    print("Indexing complete.")
    save_index_report(file_data, errors)

def calculate_file_score(file_data, frequent_terms):
    score = 0
    path = file_data['path']
    extension = file_data['extension']

    score -= len(path)

    if "writing" in path:
        score += 3

    if any(term in path for term in frequent_terms):
        score += 2  # boost for matching popular query terms

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


def save_index_report(file_data, errors=None):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entries = [
        f"Indexing started at {timestamp}",
        f"Indexed {len(file_data)} files.",
        f"Indexing complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]

    if errors:
        log_entries.append("Errors during indexing:")
        log_entries.extend(errors)

    if config.REPORT_FORMAT == "json":
        report_data = {
            "log": log_entries,
            "files": [
                {"path": row[0], "name": row[1], "extension": row[2]} for row in file_data
            ]
        }
        path = f"{config.REPORT_PATH}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"Index report saved as JSON to {path}")

    elif config.REPORT_FORMAT == "text":
        path = f"{config.REPORT_PATH}.txt"
        with open(path, "w", encoding="utf-8") as f:
            for entry in log_entries:
                f.write(entry + "\n")
            f.write("\nFiles indexed:\n")
            for row in file_data:
                f.write(f"- {row[0]} ({row[1]}, {row[2]})\n")
        print(f"Index report saved as TXT to {path}")
