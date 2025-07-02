from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import text
from typing import List, Any, Dict, Union
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class SQLExecInfo:
    def __init__(self, sql: str, status: str, result: Union[str, Any] = None):
        self.sql = sql
        self.status = status
        self.result = result

    def to_dict(self):
        return {
            "sql": self.sql,
            "status": self.status,
            "result": str(self.result) if self.result is not None else None
        }

async def execute_sql_query_async(query: str, engine: Engine, db_path: str, timeout: int = 60) -> SQLExecInfo:
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
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, # Use default ThreadPoolExecutor
            lambda: _sync_execute_sql(query, engine, db_path)
        )
        return SQLExecInfo(sql=query, status="OK", result=result)
    except asyncio.TimeoutError:
        logging.error(f"SQL query execution timed out after {timeout} seconds: {query}")
        return SQLExecInfo(sql=query, status="TIMEOUT", result=f"Execution timed out after {timeout} seconds.")
    except Exception as e:
        logging.error(f"SQL query execution failed: {query}. Error: {e}")
        return SQLExecInfo(sql=query, status="ERROR", result=str(e))

def _sync_execute_sql(query: str, engine: Engine, db_path: str) -> List[Dict[str, Any]]:
    """
    Synchronously executes a SQL query and fetches results.
    This is a helper for the async function to run in an executor.
    
    Args:
        query (str): The SQL query string to execute.
        engine (Engine): The SQLAlchemy engine connected to the database.
        db_path (str): The PostgreSQL schema path to set for the connection.
    """
    with engine.connect() as connection:
        # Set the PostgreSQL search path for this connection
        if db_path:
            connection.execute(text(f"SET search_path TO {db_path}"))
        
        # Execute the main query
        result = connection.execute(text(query))
        
        # For SELECT statements, fetch results. For DML, commit and return status.
        if result.returns_rows:
            rows = result.fetchall()
            # Convert Row objects to dictionaries for easier handling
            return [row._asdict() for row in rows]
        else:
            connection.commit()
            return {"message": "Command executed successfully", "rowcount": result.rowcount}

async def execute_sql_queries_async(queries: List[str], engine: Engine, db_path: str, timeout: int = 60) -> List[SQLExecInfo]:
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
    tasks = [execute_sql_query_async(query, engine, db_path, timeout) for query in queries]
    return await asyncio.gather(*tasks)