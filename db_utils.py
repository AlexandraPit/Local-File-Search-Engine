import psycopg2

def connect_to_db(db_name, user, password, host, port):
    """Connects to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
          dbname=db_name,
          user=user,
          password=password,
          host=host,
          port=port
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None