from db_utils import connect_to_db


def is_txt_file(file_path, **db):
    conn = connect_to_db(**db)
    if not conn:
        return False
    with conn.cursor() as cur:
        cur.execute("SELECT extension FROM files WHERE path = %s", (file_path,))
        result = cur.fetchone()
    conn.close()
    return result and result[0] == ".txt"


def get_file_preview(file_path, **db):
    conn = connect_to_db(**db)
    if not conn:
        return "(No preview)"

    with conn.cursor() as cur:
        cur.execute("SELECT content FROM files WHERE path = %s", (file_path,))
        result = cur.fetchone()

    conn.close()

    if result and result[0]:
        lines = result[0].splitlines()[:3]   # Get the first three lines
        return "\n".join(lines)
    return "(No content)"
