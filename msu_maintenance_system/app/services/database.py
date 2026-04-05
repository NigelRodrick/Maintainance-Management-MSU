import os
from contextlib import contextmanager


def _build_odbc_connection_string():
    server = os.environ.get('DB_SERVER', 'localhost')
    database = os.environ.get('DB_NAME', 'CentralServices_AM_DB')
    user = os.environ.get('DB_USER', '')
    password = os.environ.get('DB_PASSWORD', '')
    if user and password:
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};DATABASE={database};"
            f"UID={user};PWD={password};TrustServerCertificate=yes;"
        )
    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};DATABASE={database};"
        f"Trusted_Connection=yes;TrustServerCertificate=yes;"
    )


class DatabaseService:
    """Legacy raw ODBC access for SQL Server. Not used when running on SQLite."""

    def __init__(self):
        self.connection_string = _build_odbc_connection_string()

    @contextmanager
    def get_connection(self):
        import pyodbc

        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor, conn
            except Exception as e:
                conn.rollback()
                raise e

    def execute_query(self, query, params=None):
        with self.get_cursor() as (cursor, conn):
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def execute_update(self, query, params=None):
        with self.get_cursor() as (cursor, conn):
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query, params=None):
        with self.get_cursor() as (cursor, conn):
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid if hasattr(cursor, 'lastrowid') else None


db_service = DatabaseService()
