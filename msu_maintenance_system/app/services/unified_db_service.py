"""
Unified Database Service

Bridges SQLAlchemy and raw pyodbc to provide a single, consistent
database interface while allowing gradual migration.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import pandas as pd

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from .database import db_service as legacy_db_service

# Setup logger
logger = logging.getLogger('unified_db_service')


class UnifiedDatabaseService:
    """
    Unified database service that provides a single interface
    for both SQLAlchemy and legacy pyodbc operations.
    """
    
    def __init__(self):
        self.use_sqlalchemy = True  # Prefer SQLAlchemy
        self.fallback_to_pyodbc = True  # Enable fallback for compatibility
        self.log_operations = True
    
    @contextmanager
    def get_session(self):
        """Get SQLAlchemy session with error handling."""
        session = None
        try:
            session = db.session
            yield session
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"SQLAlchemy session error: {str(e)}")
            raise
        finally:
            # Session is managed by Flask-SQLAlchemy, don't close it here
            pass
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """
        Execute a SELECT query using preferred method with fallback.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of query results
        """
        if self.use_sqlalchemy:
            try:
                with self.get_session() as session:
                    result = session.execute(text(query), params or ())
                    data = result.fetchall()
                    
                    if self.log_operations:
                        logger.info(f"SQLAlchemy query returned {len(data)} rows")
                    
                    # Convert SQLAlchemy Row objects to dictionaries
                    return [dict(row._mapping) for row in data]
                    
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy query failed: {str(e)}")
                if self.fallback_to_pyodbc:
                    logger.info("Falling back to pyodbc")
                    return self._execute_query_pyodbc(query, params)
                else:
                    raise
        
        # Fallback to pyodbc
        return self._execute_query_pyodbc(query, params)
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query using preferred method with fallback.
        
        Args:
            query: SQL query string  
            params: Query parameters tuple
            
        Returns:
            Number of affected rows
        """
        if self.use_sqlalchemy:
            try:
                with self.get_session() as session:
                    result = session.execute(text(query), params or ())
                    session.commit()
                    rowcount = result.rowcount
                    
                    if self.log_operations:
                        logger.info(f"SQLAlchemy update affected {rowcount} rows")
                    
                    return rowcount
                    
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy update failed: {str(e)}")
                if self.fallback_to_pyodbc:
                    logger.info("Falling back to pyodbc")
                    return self._execute_update_pyodbc(query, params)
                else:
                    raise
        
        # Fallback to pyodbc
        return self._execute_update_pyodbc(query, params)
    
    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """
        Execute INSERT query and return last row ID using preferred method with fallback.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Last inserted row ID or None
        """
        if self.use_sqlalchemy:
            try:
                with self.get_session() as session:
                    result = session.execute(text(query), params or ())
                    session.commit()
                    
                    # Get last inserted ID
                    if result.lastrowid:
                        row_id = result.lastrowid
                    else:
                        # For SQL Server, use SCOPE_IDENTITY()
                        identity_result = session.execute(text("SELECT SCOPE_IDENTITY()"))
                        row_id = identity_result.scalar()
                    
                    if self.log_operations:
                        logger.info(f"SQLAlchemy insert ID: {row_id}")
                    
                    return row_id
                    
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy insert failed: {str(e)}")
                if self.fallback_to_pyodbc:
                    logger.info("Falling back to pyodbc")
                    return self._execute_insert_pyodbc(query, params)
                else:
                    raise
        
        # Fallback to pyodbc
        return self._execute_insert_pyodbc(query, params)
    
    def read_sql(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """
        Execute query and return pandas DataFrame using preferred method with fallback.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            pandas DataFrame with query results
        """
        if self.use_sqlalchemy:
            try:
                with self.get_session() as session:
                    df = pd.read_sql(query, session.bind, params=params)
                    
                    if self.log_operations:
                        logger.info(f"SQLAlchemy read_sql DataFrame shape: {df.shape}")
                    
                    return df
                    
            except Exception as e:
                logger.error(f"SQLAlchemy read_sql failed: {str(e)}")
                if self.fallback_to_pyodbc:
                    logger.info("Falling back to pyodbc")
                    return self._read_sql_pyodbc(query, params)
                else:
                    raise
        
        # Fallback to pyodbc
        return self._read_sql_pyodbc(query, params)
    
    # Legacy pyodbc fallback methods
    def _execute_query_pyodbc(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """Execute query using pyodbc as fallback."""
        try:
            result = legacy_db_service.execute_query(query, params)
            
            if self.log_operations:
                logger.info(f"pyodbc fallback returned {len(result)} rows")
            
            return result
        except Exception as e:
            logger.error(f"pyodbc fallback failed: {str(e)}")
            raise
    
    def _execute_update_pyodbc(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute update using pyodbc as fallback."""
        try:
            result = legacy_db_service.execute_update(query, params)
            
            if self.log_operations:
                logger.info(f"pyodbc fallback affected {result} rows")
            
            return result
        except Exception as e:
            logger.error(f"pyodbc fallback failed: {str(e)}")
            raise
    
    def _execute_insert_pyodbc(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """Execute insert using pyodbc as fallback."""
        try:
            result = legacy_db_service.execute_insert(query, params)
            
            if self.log_operations:
                logger.info(f"pyodbc fallback inserted ID: {result}")
            
            return result
        except Exception as e:
            logger.error(f"pyodbc fallback failed: {str(e)}")
            raise
    
    def _read_sql_pyodbc(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Execute read_sql using pyodbc as fallback."""
        try:
            # Use the legacy database connection string
            import pyodbc
            
            conn = pyodbc.connect(
                "DRIVER={SQL Server};"
                "SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;"
                "DATABASE=CentralServices_AM_DB;"
                "Trusted_Connection=yes;"
            )
            
            try:
                df = pd.read_sql(query, conn, params=params)
                
                if self.log_operations:
                    logger.info(f"pyodbc fallback DataFrame shape: {df.shape}")
                
                return df
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"pyodbc read_sql fallback failed: {str(e)}")
            raise


# Create global instance
unified_db_service = UnifiedDatabaseService()


# Backward compatibility functions
def execute_query(query: str, params: Optional[Tuple] = None) -> List[Any]:
    """Legacy compatibility function."""
    return unified_db_service.execute_query(query, params)


def execute_update(query: str, params: Optional[Tuple] = None) -> int:
    """Legacy compatibility function."""
    return unified_db_service.execute_update(query, params)


def execute_insert(query: str, params: Optional[Tuple] = None) -> Optional[int]:
    """Legacy compatibility function."""
    return unified_db_service.execute_insert(query, params)
