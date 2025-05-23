# db_msql_converter.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from config import Config # Assuming config.py is in the same directory

# Load environment variables
load_dotenv()

class DatabaseSchemaConverter:
    def __init__(self, database_uri=None):
        """
        Initializes the converter with a database URI.
        If no URI is provided, it uses the one from Config.
        """
        self.database_uri = database_uri if database_uri else Config.DATABASE_URI
        self.engine = create_engine(self.database_uri)

    def get_table_names(self):
        """
        Retrieves a list of all table names in the database.
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def get_table_description(self, table_name):
        """
        Retrieves the schema description for a given table.
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        # You might also want to get foreign keys, primary keys, etc.
        # foreign_keys = inspector.get_foreign_keys(table_name)
        # primary_key = inspector.get_pk_constraint(table_name)

        description = f"Table: {table_name}\n"
        for col in columns:
            description += f"  - {col['name']} ({col['type']})\n"
        # Add foreign key and primary key info if needed
        return description

    def convert_to_msql_description(self, table_descriptions):
        """
        Converts table descriptions to a text-to-SQL friendly format (placeholder for M-SQL).
        This is a basic representation. Replace with actual M-SQL procedure if found.
        """
        msql_output = ""
        for description in table_descriptions:
            msql_output += description + "\n"
        return msql_output.strip()

    def process_database(self):
        """
        Processes the entire database to get table descriptions and convert them.
        """
        table_names = self.get_table_names()
        table_descriptions = []
        for table_name in table_names:
            description = self.get_table_description(table_name)
            table_descriptions.append(description)

        msql_representation = self.convert_to_msql_description(table_descriptions)
        return msql_representation

# Example Usage (optional, for testing)
if __name__ == "__main__":
    converter = DatabaseSchemaConverter()
    msql_schema = converter.process_database()
    print("--- M-SQL Schema Description ---")
    print(msql_schema)
    print("------------------------------")