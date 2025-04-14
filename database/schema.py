# database/schema.py
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

        create_table_sql = """
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                path TEXT NOT NULL,
                name TEXT NOT NULL,
                extension TEXT,
                content TEXT,
                content_tsvector TSVECTOR
            );
        """

        create_index_sql = """
            CREATE INDEX IF NOT EXISTS idx_content_tsvector 
            ON files USING GIN(content_tsvector);
        """

        cur.execute(create_table_sql)
        cur.execute(create_index_sql)

        conn.commit()
        print("Database schema created.")

    except psycopg2.Error as e:
        print(f"Error setting up database: {e}")

    finally:
        if cur: cur.close()
        if conn: conn.close()
