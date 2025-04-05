import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import DB_SETTINGS

# Database configuration
DB_CONFIG = DB_SETTINGS

@contextmanager
def get_db_connection():
    """Create a database connection context manager"""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor():
    """Create a database cursor context manager"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

class Database:
    def __init__(self):
        self.config = DB_CONFIG
    
    def execute(self, query, params=None):
        """Execute a query and return results"""
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return None
    
    def execute_one(self, query, params=None):
        """Execute a query and return first result"""
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchone()
            return None
    
    def execute_many(self, query, params_list):
        """Execute a query with multiple parameter sets"""
        with get_db_cursor() as cursor:
            cursor.executemany(query, params_list)
            if cursor.description:
                return cursor.fetchall()
            return None
    
    def transaction(self):
        """Create a transaction context"""
        return get_db_cursor()

# Create global database instance
db = Database() 