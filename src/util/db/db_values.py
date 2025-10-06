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
    Gets all unique values for a given database with less restrictive filtering.

    Args:
        db_id: The ID of the database.

    Returns:
        A dictionary containing the unique values for each table and column.
    """
    # --- Configurable Thresholds (Tune these values to adjust restrictiveness) ---
    # Exclude columns with more than this many unique values (high cardinality).
    MAX_DISTINCT_VALUES = 5000
    # Exclude columns where the total size of text data exceeds this limit (in bytes).
    MAX_TOTAL_NAME_LENGTH = 5_000_000  # 5 MB
    MAX_TOTAL_LENGTH = 3_000_000  # 2 MB
    MAX_DISTINCT_VALUES = 150
    # Exclude columns where the average value length is very high (e.g., descriptions, blobs).
    MAX_AVERAGE_LENGTH = 50
    # Exclude columns that are very unlikely to be useful categorical features.
    EXCLUDED_KEYWORDS = ["id", "_id", "url", "email", "web", "phone", "date", "address", "time"]

    db_manager = DatabaseManager()
    engine = db_manager.create_engine(db_id)
    
    unique_values = {}
    inspector = inspect(engine)
    
    # Use a single connection for all operations for a massive performance boost
    with engine.connect() as connection:
        table_names = inspector.get_table_names()
        
        for table_name in table_names:
            if table_name == "sqlite_sequence":
                continue
            
            unique_values[table_name] = {}
            columns = inspector.get_columns(table_name)
            primary_keys = [key for key in inspector.get_pk_constraint(table_name)['constrained_columns']]

            for column in columns:
                column_name = column['name']
                column_name_lower = column_name.lower()

                # --- A series of clear "guard clauses" to skip columns ---

                # 1. Skip primary keys
                if column_name in primary_keys:
                    continue

                # 2. Skip non-text columns
                if "TEXT" not in str(column['type']):
                    continue

                # 3. Skip columns based on keywords and common ID patterns
                if any(keyword in column_name_lower for keyword in EXCLUDED_KEYWORDS) or \
                   "id" in column_name_lower or column_name_lower.endswith("id"):
                    continue

                try:
                    # 4. Perform data-based checks to exclude very large columns
                    query = text(f'''
                        SELECT 
                            SUM(LENGTH("{column_name}")), 
                            COUNT(*)
                        FROM (
                            SELECT DISTINCT "{column_name}"
                            FROM "{table_name}"
                            WHERE "{column_name}" IS NOT NULL
                        ) AS distinct_values
                    ''')
                    result = connection.execute(query).fetchone()
                    sum_of_lengths, count_distinct = result[0], result[1]

                    if sum_of_lengths is None or not count_distinct:
                        continue
                    
                    average_length = sum_of_lengths / count_distinct

                    # Skip columns that exceed limits
                    skip_column = (
                        ("name" in column_name_lower and sum_of_lengths < MAX_TOTAL_NAME_LENGTH)
                        or (sum_of_lengths < MAX_TOTAL_LENGTH and average_length < MAX_AVERAGE_LENGTH)
                        or count_distinct < MAX_DISTINCT_VALUES
                    )

                    if not skip_column:
                        # Fetch unique non-null values for valid columns
                        values_query = text(f'''
                            SELECT DISTINCT "{column_name}"
                            FROM "{table_name}"
                            WHERE "{column_name}" IS NOT NULL
                        ''')
                        values_result = connection.execute(values_query)
                        unique_values[table_name][column_name] = [str(row[0]) for row in values_result]

                except Exception as e:
                    logging.error(f"Error processing column {column_name} in table {table_name}: {e}")
    
    return unique_values