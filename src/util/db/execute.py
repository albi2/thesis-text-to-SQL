from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import text
from typing import List, Any, Dict, Union
import asyncio
import logging
from enum import Enum
from pydantic import BaseModel, PrivateAttr
from infrastructure.database.database_manager import db_manager
from common.config.config_helper import ConfigurationHelper
from ..constants import DatabaseConstants

logging.basicConfig(level=logging.INFO)

class SQLExecStatus(Enum):
    CORRECT_SYNTAX = "CORRECT_SYNTAX"
    INCORRECT_SYNTAX = "INCORRECT_SYNTAX"
    EMPTY_RESULT = "EMPTY_RESULT"

class SQLExecInfo(BaseModel):
    sql: str = ''
    status: SQLExecStatus = None
    result: List[Any] = []
    
    _execution_status: SQLExecStatus = PrivateAttr(default=None)
    _execution_results: List[Any] = PrivateAttr(default=[])

    def __init__(self, sql: str, status: str, result: List[Any] = []):
        self.sql = sql
        self.status = status
        self.result = result

    def to_dict(self):
        return {
            "sql": self.sql,
            "status": self.status,
            "result": str(self.result) if self.result is not None else None
        }
    
    # @property
    # def execution_result(self) -> List[Any]:
    #     if not self._execution_results:
    #         self._execution_results = _sync_execute_sql(self.sql, )
    #     else:
    #         return self._execution_results


async def execute_sql_query_async(query: str, db_path: str, timeout: int = 60) -> SQLExecInfo:
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
        # SQLAlchemy's execute is synchronous, so we run it in a thread pool executor
        # to simulate non-blocking behavior for the async context.
        # For true async DB operations, an async driver like asyncpg or aiomysql would be needed.

        # TODO: Inlcude the timeout here
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, # Use default ThreadPoolExecutor
            lambda: _sync_execute_sql(query, db_path)
        )

        if len(result) == 0:
            return SQLExecInfo(sql=query, status=SQLExecStatus.EMPTY_RESULT, result=result)
        
        return SQLExecInfo(sql=query, status=SQLExecStatus.CORRECT_SYNTAX, result=result)
        
    except asyncio.TimeoutError:
        logging.error(f"SQL query execution timed out after {timeout} seconds: {query}")
        return SQLExecInfo(sql=query, status=SQLExecStatus.SYNTACTICALLY_INCORRECT)
    except Exception as e:
        logging.error(f"SQL query execution failed: {query}. Error: {e}")
        return SQLExecInfo(sql=query, status=SQLExecStatus.SYNTACTICALLY_INCORRECT)
    


def _sync_execute_sql(query: str, db_path: str = None, fetch: Union[str, int] = 500) -> List[Dict[str, Any]]:
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

    engine = db_manager._engine

    with engine.connect() as connection:
        # Set the PostgreSQL search path for this connection
        if db_path:
            connection.execute(text(f"SET search_path TO {db_path}"))
        
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

async def execute_sql_queries_async(queries: List[str], db_path: str, timeout: int = 60) -> List[SQLExecInfo]:
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
    tasks = [execute_sql_query_async(query, db_path, timeout) for query in queries]
    return await asyncio.gather(*tasks)

def _compare_sqls_outcomes(predicted_sql: str, ground_sql: str, db_path: str) -> int:
    """
    Compares the outcomes of two SQL queries to check for equivalence.
    
    Args:
        db_path (str): The path to the database file.
        predicted_sql (str): The predicted SQL query.
        ground_truth_sql (str): The ground truth SQL query.
        
    Returns:
        int: 1 if the outcomes are equivalent, 0 otherwise.
    
    Raises:
        Exception: If an error occurs during SQL execution.
    """
    try:
        predicted_res = _sync_execute_sql(predicted_sql, db_path=db_path)
        ground_truth_res = _sync_execute_sql(ground_sql, db_path=db_path)
        return int(set(predicted_res) == set(ground_truth_res))
    except Exception as e:
        logging.critical(f"Error comparing SQL outcomes: {e}")
        raise e
    
    
