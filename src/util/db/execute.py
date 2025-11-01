from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import text
from typing import List, Any, Dict, Union
import asyncio
import hashlib
import json
import logging
from enum import Enum
from ..constants import DatabaseConstants

logging.basicConfig(level=logging.INFO)

class SQLExecStatus(Enum):
    CORRECT_SYNTAX = "CORRECT_SYNTAX"
    INCORRECT_SYNTAX = "INCORRECT_SYNTAX"
    EMPTY_RESULT = "EMPTY_RESULT"

class SQLExecInfo:
    sql: str = ''
    status: SQLExecStatus = None
    result: List[Any] = []
    error_message: str = None

    def __init__(self, sql: str, status: str = None, result: List[Any] = [], error_message: str = None):
        self.sql = sql
        self.status = status
        self.result = result
        self.error_message = error_message

    def to_dict(self):
        return {
            "sql": self.sql,
            "status": self.status.value if self.status is not None else None,
            "result": str(self.result) if self.result is not None else None,
            "error_message": self.error_message
        }
    
    # @property
    # def execution_result(self) -> List[Any]:
    #     if not self._execution_results:
    #         self._execution_results = _sync_execute_sql(self.sql, )
    #     else:
    #         return self._execution_results


async def execute_sql_query_async(
    query: str,
    db_path: str,
    engine: Engine,
    timeout: int = 60
) -> SQLExecInfo:
    """
    Executes a SQL query asynchronously against the provided database engine.

    Args:
        query (str): The SQL query string to execute.
        engine (Engine): The SQLAlchemy engine connected to the database.
        db_path (str): The database path/schema to set for the connection.
        timeout (int): The maximum time in seconds to wait for query execution.

    Returns:
        SQLExecInfo: An object containing the SQL query, status, and result/error.
    """
    try:
        # ✅ Use asyncio.wait_for + asyncio.to_thread to enforce timeout cleanly
        result = await asyncio.wait_for(
            asyncio.to_thread(_sync_execute_sql, query, engine, db_path),
            timeout=timeout
        )

        if len(result) == 0:
            return SQLExecInfo(
                sql=query,
                status=SQLExecStatus.EMPTY_RESULT,
                result=result
            )

        return SQLExecInfo(
            sql=query,
            status=SQLExecStatus.CORRECT_SYNTAX,
            result=result
        )

    except asyncio.TimeoutError:
        logging.warning(f"SQL query execution timed out after {timeout}s: {query}")
        return SQLExecInfo(
            sql=query,
            status=SQLExecStatus.INCORRECT_SYNTAX,
            error_message="Query execution timed out."
        )
    except Exception as e:
        logging.error(f"SQL query execution failed: {query}. Error: {e}")
        return SQLExecInfo(
            sql=query,
            status=SQLExecStatus.INCORRECT_SYNTAX,
            error_message=str(e)
        )
    


def _sync_execute_sql(query: str, engine: Engine, db_path: str = None, fetch: Union[str, int] = 500) -> List[Dict[str, Any]]:
    """
    Synchronously executes a SQL query and fetches results.
    This is a helper for the async function to run in an executor.
    
    Args:
        query (str): The SQL query string to execute.
        engine (Engine): The SQLAlchemy engine connected to the database.
        db_path (str): The PostgreSQL schema path to set for the connection.
    """

    if db_path is None:
        db_path = DatabaseConstants.DB_PATH

    with engine.connect() as connection:
        # Set the PostgreSQL search path for this connection
        
        # Execute the main query
        result = connection.execute(text(query))

        if not result.returns_rows:
            connection.commit()
            return []

        
        # For SELECT statements, fetch results. For DML, commit and return status.
        if fetch == "all":
            rows = result.fetchall()
        elif fetch == "one":
            rows = result.fetchone()
        elif isinstance(fetch, int):
            rows = result.fetchmany(fetch)
        
    return [row._asdict() for row in rows]

async def execute_sql_queries_async(queries: List[str], db_path: str, engine: Engine, timeout: int = 60) -> List[SQLExecInfo]:
    """
    Executes a list of SQL queries asynchronously and returns their execution information.

    Args:
        queries (List[str]): A list of SQL query strings to execute.
        engine (Engine): The SQLAlchemy engine connected to the database.
        db_path (str): The database path/schema to set for the connection.
        timeout (int): The maximum time in seconds to wait for each query execution.

    Returns:
        List[SQLExecInfo]: A list of SQLExecInfo objects for each query.
    """
    sem = asyncio.Semaphore(5)


    async with sem:
        tasks = [execute_sql_query_async(query, db_path, engine, timeout) for query in queries]
        return await asyncio.gather(*tasks)

def compare_sqls_outcomes(sql_1: str, sql_2: str, db_path: str, engine: Engine) -> int:
    """
    Compares the outcomes of two SQL queries to check for equivalence.
    
    Args:
        db_path (str): The path to the database file.
        sql_1 (str): The first SQL query.
        sql_2 (str): The second SQL query.
        
    Returns:
        int: 1 if the outcomes are equivalent, 0 otherwise.
    
    Raises:
        Exception: If an error occurs during SQL execution.
    """
    try:
        result_1 = _sync_execute_sql(sql_1, engine, db_path=db_path)
        result_2 = _sync_execute_sql(sql_2, engine, db_path=db_path)

        if len(result_1) != len(result_2):
            return 0
        
        if len(result_1) == 0:
            return 1

        if len(result_1[0]) != len(result_2[0]):
            return 0

        def sort_and_hash_ignore_col_order(result):
            if not result:
                return ""

            def safe_sort_key(value):
                """Convert value to a sortable format, handling None"""
                if value is None:
                    return (0, '')  # None sorts first
                elif isinstance(value, str):
                    return (1, value)
                elif isinstance(value, (int, float)):
                    return (2, value)
                else:
                    return (3, str(value))

            # Sort values within each row (ignore column order)
            rows_as_tuples = [tuple(sorted(row.values(), key=safe_sort_key)) for row in result]

            # Sort rows (so row order doesn't matter)
            sorted_rows = sorted(rows_as_tuples, key=lambda row: tuple(safe_sort_key(val) for val in row))

            # Hash final representation
            return hashlib.md5(json.dumps(sorted_rows, sort_keys=True, default=str).encode()).hexdigest()

        hash_1 = sort_and_hash_ignore_col_order(result_1)
        hash_2 = sort_and_hash_ignore_col_order(result_2)

        return int(hash_1 == hash_2)
    except Exception as e:
        logging.critical(f"Error comparing SQL outcomes: {e}")
        return 0
    
    
