import os
import logging
from typing import Dict, List
from sqlalchemy import text, inspect
from infrastructure.database.database_manager import DatabaseManager
from util.constants import DatabaseConstants

def get_all_db_ids() -> List[str]:
    """
    Gets all database IDs from the filesystem.

    Returns:
        A list of database IDs.
    """
    db_path = DatabaseConstants.SQLITE_PATH.split("sqlite:///")[-1]
    return [f.name for f in os.scandir(db_path) if f.is_dir()]

def get_unique_values_for_db(db_id: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Gets all unique values for a given database.

    Args:
        db_id: The ID of the database.

    Returns:
        A dictionary containing the unique values for each table and column.
    """
    db_manager = DatabaseManager()
    engine = db_manager.create_engine(db_id)
    
    unique_values = {}
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    for table_name in table_names:
        if table_name == "sqlite_sequence":
            continue
        
        unique_values[table_name] = {}
        columns = inspector.get_columns(table_name)
        primary_keys = [key for key in inspector.get_pk_constraint(table_name)['constrained_columns']]

        for column in columns:
            column_name = column['name']
            
            if column_name in primary_keys:
                continue

            if "TEXT" not in str(column['type']):
                continue

            if any(keyword in column_name.lower() for keyword in ["_id", " id", "url", "email", "web", "time", "phone", "date", "address"]) or column_name.lower().endswith("Id"):
                continue

            with engine.connect() as connection:
                try:
                    result = connection.execute(text(f'SELECT SUM(LENGTH("{column_name}")), COUNT(DISTINCT "{column_name}") FROM "{table_name}" WHERE "{column_name}" IS NOT NULL')).fetchone()
                    sum_of_lengths, count_distinct = result[0], result[1]

                    if sum_of_lengths is None or count_distinct == 0:
                        continue

                    average_length = sum_of_lengths / count_distinct
                    
                    if ("name" in column_name.lower() and sum_of_lengths < 5000000) or (sum_of_lengths < 2000000 and average_length < 25) or count_distinct < 100:
                        values_result = connection.execute(text(f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL'))
                        unique_values[table_name][column_name] = [str(row[0]) for row in values_result]
                except Exception as e:
                    logging.error(f"Error processing column {column_name} in table {table_name}: {e}")

    db_manager.close_connections(engine)
    return unique_values