import psycopg2
from constants import DATABASE_URL

URL = DATABASE_URL
CONN = psycopg2.connect(URL)

def execute_commit(connection, sql, params=None):
    cursor = connection.cursor()
    cursor.execute(sql, params or ())
    connection.commit()
    cursor.close()

def execute_query(connection, sql, params=None):
    cursor = connection.cursor()
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    cursor.close()
    return rows
