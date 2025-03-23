import os
import psycopg2
from db_utils import connect_to_db

def crawl_and_index(root_dir, db_name, user, password, host, port):
    """
    Crawls the file system, extracts data, and indexes it in PostgreSQL.

    Args:
        root_dir (str): The directory to start crawling from.
        db_name (str): The name of the PostgreSQL database.
        user (str): PostgreSQL username.
        password (str): PostgreSQL password.
        host (str): PostgreSQL host.
        port (str): PostgreSQL port.
    """

    conn = connect_to_db(db_name, user, password, host, port)
    if conn:
        cursor = conn.cursor()

        try:
            # Create the files table (if it doesn't exist)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    name TEXT,
                    extension TEXT,
                    content TEXT,
                    content_tsvector tsvector  -- Add tsvector column
                    -- Add other metadata fields as needed
                )
            """)

            # Create the index (if it doesn't exist)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_content_tsvector ON files USING GIN (content_tsvector);
            """)

            for root, _, files in os.walk(root_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # 1. Filter (Example: Only process .txt files)
                        if not file.endswith(".txt"):
                            continue

                        # 2. Extract Data
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # 3. Get Metadata
                        name = os.path.splitext(file)[0]
                        extension = os.path.splitext(file)[1]

                        # 4. Store in Database (and update tsvector)
                        cursor.execute("""
                            INSERT INTO files (path, name, extension, content, content_tsvector)
                            VALUES (%s, %s, %s, %s, to_tsvector('english', %s))
                            ON CONFLICT (path) DO UPDATE 
                            SET name = %s, extension = %s, content = %s, content_tsvector = to_tsvector('english', %s)
                        """, (file_path, name, extension, content, content, name, extension, content, content))

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

            conn.commit()
            print("Indexing complete.")

        except psycopg2.Error as e:
            print(f"Database error: {e}")

        finally:
            cursor.close()
            conn.close()
    else:
        print("Indexing failed: Could not connect to the database.")