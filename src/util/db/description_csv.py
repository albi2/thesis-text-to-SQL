import os
import csv
from typing import Dict
from util.constants import DatabaseConstants
from util.db.database_descriptor import DatabaseDescriptor

def load_database_descriptions(db_id: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Loads the database descriptions from the CSV files.

    Args:
        db_id: The ID of the database.

    Returns:
        A dictionary containing the database descriptions.
    """
    db_descriptions = {}
    db_path = os.path.join(DatabaseConstants.COLUMN_DESCRIPTIONS, db_id)
    if not os.path.exists(db_path):
        return db_descriptions

    for table_file in os.listdir(db_path):
        if table_file.endswith(".csv"):
            table_name = os.path.splitext(table_file)[0]
            db_descriptions[table_name] = {}
            with open(os.path.join(db_path, table_file), "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    column_name = row.get('original_column_name', '')
                    
                    # Preprocess column_description
                    column_description = row.get('column_description', '')
                    if column_description:
                        column_description = column_description.replace('\n', ' ').replace("commonsense evidence:", "").strip()
                    
                    # Preprocess value_description
                    value_description = row.get('value_description', '')
                    if value_description:
                        value_description = value_description.replace('\n', ' ').replace("commonsense evidence:", "").strip()
                        if value_description.lower().startswith("not useful"):
                            value_description = value_description[10:].strip()
                    
                    processed_row = {
                        'original_column_name': column_name,
                        'column_name': row.get('column_name', '').strip(),
                        'column_description': column_description,
                        'data_format': row.get('data_format', '').strip(),
                        'value_description': value_description
                    }
                    db_descriptions[table_name][column_name] = processed_row
    return db_descriptions

def load_database_descriptor(db_id: str) -> DatabaseDescriptor:
    """
    Loads the database descriptions and converts them to a DatabaseDescriptor object.

    Args:
        db_id: The ID of the database.

    Returns:
        A DatabaseDescriptor object.
    """
    db_descriptions_dict = load_database_descriptions(db_id)
    return DatabaseDescriptor.from_dictionary(db_id, db_descriptions_dict)