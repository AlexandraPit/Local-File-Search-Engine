import psycopg2

def setup_database(host, port, dbname, user, password):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                path TEXT NOT NULL,
                name TEXT NOT NULL,
                extension TEXT,
                content TEXT,
                content_tsvector TSVECTOR
            );
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_content_tsvector ON files USING GIN(content_tsvector);")

        conn.commit()
        cur.close()
        conn.close()
        print("Database setup complete.")
    except psycopg2.Error as e:
        print(f"Error setting up database: {e}")

def clear_database(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM files")
        conn.commit()
    print("Database cleared.")

