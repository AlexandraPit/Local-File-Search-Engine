from database.db_utils import connect_to_db
from indexer.crawler import crawl_files
from indexer.report import save_index_report

def crawl_and_index(root_path, **db):
    conn = connect_to_db(**db)
    if not conn:
        print("Failed to connect to database.")
        return

    with conn.cursor() as curr:
        curr.execute("DELETE FROM files")
        file_data, errors = crawl_files(root_path)

        insert_query = """
            INSERT INTO files (path, name, extension, content, content_tsvector)
            VALUES (%s, %s, %s, %s, to_tsvector('english', %s))
        """
        curr.executemany(insert_query, file_data)
        conn.commit()

    conn.close()
    print("Indexing complete.")
    save_index_report(file_data, errors)
