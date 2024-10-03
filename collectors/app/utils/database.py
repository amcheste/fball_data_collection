import psycopg

def connect():
    # TODO read from env variables
    conn = psycopg.connect(
        # host='localhost', #TODO envvars
            host='database',
            port=5432,
            dbname='nfl_data',
            user='nfl_data',
            password='nfl_data'
    )
    cur = conn.cursor()
    return cur, conn