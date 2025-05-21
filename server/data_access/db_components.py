import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from .constants import DATABASE_URL

# Create a connection pool with a minimum of 1 and maximum of 10 connections
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL,
    sslmode='require' if 'RENDER' in os.environ else 'prefer'
)

def get_connection():
    """Get a connection from the connection pool"""
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        # Try to create a new connection if pool is empty
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            print(f"Failed to create new connection: {e}")
            raise

def release_connection(conn):
    """Release a connection back to the pool"""
    try:
        connection_pool.putconn(conn)
    except Exception as e:
        print(f"Error releasing connection: {e}")
        try:
            conn.close()
        except:
            pass

def execute_commit(sql, params=None):
    """Execute a query that modifies data (INSERT, UPDATE, DELETE)"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error in execute_commit: {e}")
        raise
    finally:
        if conn:
            release_connection(conn)

def execute_query(sql, params=None):
    """Execute a query that returns data (SELECT)"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
    except Exception as e:
        print(f"Error in execute_query: {e}")
        raise
    finally:
        if conn:
            release_connection(conn)

def execute_query_one(sql, params=None):
    """Execute a query that returns a single row"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()
    except Exception as e:
        print(f"Error in execute_query_one: {e}")
        raise
    finally:
        if conn:
            release_connection(conn)
