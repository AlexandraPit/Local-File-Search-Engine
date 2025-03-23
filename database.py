import psycopg2
from db_utils import connect_to_db

def clear_database(db_name, user, password, host, port):
    """Deletes all indexed files from the database."""
    conn = connect_to_db(db_name, user, password, host, port)
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM files;")  # Clears all indexed data
            conn.commit()
            print("Database cleared on exit.")
        except psycopg2.Error as e:
            print(f"Error clearing database: {e}")
        finally:
            cursor.close()
            conn.close()

def get_file_preview(db_name, user, password, host, port, file_path):
    """
    Fetches a short preview of the file content from the database.

    Args:
        db_name (str): The name of the PostgreSQL database.
        user (str): PostgreSQL username.
        password (str): PostgreSQL password.
        host (str): PostgreSQL host.
        port (str): PostgreSQL port.
        file_path (str): The path of the selected file.

    Returns:
        str: A preview of the file content (first 3 words).
    """
    conn = connect_to_db(db_name, user, password, host, port)
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT content FROM files WHERE path = %s", (file_path,))
            result = cursor.fetchone()
            if result:
                content = result[0]
                return " ".join(content.split())   # First 3 words
            return "(No content)"
        except psycopg2.Error as e:
            print(f"Database error during preview: {e}")
            return "(Error fetching preview)"
        finally:
            cursor.close()
            conn.close()
    return "(No preview available)"


def search_files(db_name, user, password, host, port, query):
    """
    Searches the database for files matching the query using PostgreSQL's full-text search.

    Args:
        db_name (str): The name of the PostgreSQL database.
        user (str): PostgreSQL username.
        password (str): PostgreSQL password.
        host (str): PostgreSQL host.
        port (str): PostgreSQL port.
        query (str): The search query string.

    Returns:
        list: A list of file paths that match the query.
    """

    conn = connect_to_db(db_name, user, password, host, port)
    if conn:
        cursor = conn.cursor()

        try:
            # 1. Construct the full-text search query
            ts_query = " & ".join(query.split())  # Combine words with the AND operator

            # 2. Execute the query
            cursor.execute("""
                SELECT path, substring(content FROM 1 FOR 50)
                FROM files
                WHERE (content_tsvector @@ to_tsquery('english', %s)) 
                   OR (name ILIKE %s)
            """, (ts_query, f"%{query}%"))

            # 3. Fetch the results
            results = cursor.fetchall()

            return results

        except psycopg2.Error as e:
            print(f"Database error during search: {e}")
            return# Return an empty list in case of an error

        finally:
            cursor.close()
            conn.close()
    else:
        print("Search failed: Could not connect to the database.")
        return
