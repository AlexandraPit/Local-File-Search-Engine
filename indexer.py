import os
import psycopg2
from db_utils import connect_to_db

def crawl_and_index(root_dir, db_name, user, password, host, port):
    """
    Crawls the file system, extracts data, and indexes it in PostgreSQL.
    Index all files, but only read content for .txt files.
    Also updates entries if files are modified and deletes entries for files no longer in the folder.

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
                    content_tsvector tsvector,
                    last_modified TIMESTAMP
                )
            """)

            # Create the index (if it doesn't exist)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_content_tsvector ON files USING GIN (content_tsvector);
            """)

            # Get a list of files currently in the database
            cursor.execute("SELECT path FROM files")
            indexed_files = set()  # Keep track of indexed files

            # Crawl the file system
            for root, _, files in os.walk(root_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Filter to include all file types
                        # Read content and preview only for .txt files

                        extension = os.path.splitext(file)[1].lower() #mime-type

                        # Extract metadata
                        name = os.path.splitext(file)[0]
                        last_modified = os.path.getmtime(file_path)  # Unix timestamp

                        # Handle .txt files (read content and store)
                        if extension == ".txt":
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            cursor.execute("SELECT last_modified FROM files WHERE path = %s", (file_path,))
                            result = cursor.fetchone()

                            if result:
                                stored_modified_time = result[0]
                                if stored_modified_time >= last_modified:
                                    indexed_files.add(file_path)
                                    continue  # No need to update

                                # Update existing file
                                cursor.execute(""" 
                                    UPDATE files 
                                    SET name=%s, extension=%s, content=%s, content_tsvector=to_tsvector('english', %s), last_modified=to_timestamp(%s)
                                    WHERE path=%s
                                """, (name, extension, content, content, last_modified, file_path))
                            else:
                                # Insert new file
                                cursor.execute("""
                                    INSERT INTO files (path, name, extension, content, content_tsvector, last_modified)
                                    VALUES (%s, %s, %s, %s, to_tsvector('english', %s), to_timestamp(%s))
                                """, (file_path, name, extension, content, content, last_modified))

                            indexed_files.add(file_path)

                        else:
                            # For non-txt files, store metadata and set content_tsvector to NULL
                            cursor.execute("SELECT last_modified FROM files WHERE path = %s", (file_path,))
                            result = cursor.fetchone()

                            if result:
                                stored_modified_time = result[0]
                                if stored_modified_time >= last_modified:  # File hasn't changed, skip it
                                    indexed_files.add(file_path)
                                    continue  # No need to update

                                # Update existing non-txt file
                                cursor.execute("""
                                    UPDATE files 
                                    SET name=%s, extension=%s, content=NULL, content_tsvector=NULL, last_modified=to_timestamp(%s)
                                    WHERE path=%s
                                """, (name, extension, last_modified, file_path))
                            else:
                                # Insert new non-txt file
                                cursor.execute("""
                                    INSERT INTO files (path, name, extension, content, content_tsvector, last_modified)
                                    VALUES (%s, %s, %s, NULL, NULL, to_timestamp(%s))
                                """, (file_path, name, extension, last_modified))

                            indexed_files.add(file_path)

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

            # Delete removed files
            cursor.execute("SELECT path FROM files")
            stored_files = {row[0] for row in cursor.fetchall()}
            deleted_files = stored_files - indexed_files  # Find files that no longer exist

            for file_path in deleted_files:
                cursor.execute("DELETE FROM files WHERE path = %s", (file_path,))
                print(f"File {file_path} deleted from the database.")

            conn.commit()
            print("Indexing complete.")

        except psycopg2.Error as e:
            print(f"Database error: {e}")

        finally:
            cursor.close()
            conn.close()
    else:
        print("Indexing failed: Could not connect to the database.")
