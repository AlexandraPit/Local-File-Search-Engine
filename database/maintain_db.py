# database/maintenance.py

def clear_database(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM files")
            conn.commit()
        print("Database cleared.")
    except Exception as e:
        print(f"Failed to clear database: {e}")
