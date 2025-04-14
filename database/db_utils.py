import psycopg2

def connect_to_db(host, port, dbname, user, password):
    try:
        return psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None
