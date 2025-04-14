# previewing/previewer.py
from database.db_utils import connect_to_db

def get_file_preview(file_path, **db):
    conn = connect_to_db(**db)
    if not conn:
        return "(No preview)"

    with conn.cursor() as cur:
        cur.execute("SELECT content FROM files WHERE path = %s", (file_path,))
        result = cur.fetchone()

    conn.close()

    if result and result[0]:
        lines = result[0].splitlines()[:3]  # Get the first 3 lines
        return "\n".join(lines)
    return "(No content)"
