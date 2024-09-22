import psycopg

def connect():
    # TODO read from env variables
    conn = psycopg.connect(
            host='localhost',
            port=5432,
            dbname='football',
            user='user',
            password='password'
    )
    cur = conn.cursor()
    return cur, conn

