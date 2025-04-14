# previewing/file_type_checker.py
from database.db_utils import connect_to_db

def is_txt_file(file_path, **db):
    conn = connect_to_db(**db)
    if not conn:
        return False

    with conn.cursor() as cur:
        cur.execute("SELECT extension FROM files WHERE path = %s", (file_path,))
        result = cur.fetchone()

    conn.close()
    return result and result[0] == ".txt"
