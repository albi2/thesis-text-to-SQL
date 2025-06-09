"""
Script to preprocess database column information and populate a ChromaDB collection.

This script connects to a database, extracts schema information (tables and columns),
and then stores representations of these columns (name or description) into
a ChromaDB vector store. This allows for semantic searching of database columns.
"""
import logging
import argparse
from typing import List, Dict, Any
import sys
import torch
import os

from infrastructure.vector_db.chroma_client import ChromaClient
from infrastructure.database.database_manager import DatabaseManager
from components.schema.schema_engine import SchemaEngine
from components.schema.schema_engine_factory import SchemaEngineFactory
from common.config.config_helper import ConfigurationHelper
from components.models.embedding_model_facade import SentenceTransformerEmbeddingFacade
from util.constants import PreprocessingConstants

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print("CUDA cache emptied.")

os.environ['CHROMA_TELEMETRY_ANALYTICS'] = 'False'

def main(chroma_config_file: str = "chroma_db.yaml", chroma_config_path_in_file: str = "chroma_db") -> None:
    """
    Main function to extract database column information and populate ChromaDB.

    Args:
        chroma_config_file (str, optional): Name of the ChromaDB configuration file.
        chroma_config_path_in_file (str, optional): Path within the ChromaDB config file to its settings.
    """
    logging.info("Starting database column preprocessing for ChromaDB population.")


    # Initialize ConfigurationHelper for ChromaDB config
    cfg_helper = ConfigurationHelper() # Assumes default config_dir="config"

    # Load ChromaDB configuration
    chroma_settings = cfg_helper.get_config(chroma_config_file, chroma_config_path_in_file)
    chroma_host = PreprocessingConstants.DEFAULT_CHROMA_HOST
    chroma_port = PreprocessingConstants.DEFAULT_CHROMA_PORT

    if chroma_settings:
        chroma_host = chroma_settings.get("host", PreprocessingConstants.DEFAULT_CHROMA_HOST)
        chroma_port = int(chroma_settings.get("port", PreprocessingConstants.DEFAULT_CHROMA_PORT))
    else:
        logging.warning(
            f"ChromaDB configuration not found in '{chroma_config_file}' at path '{chroma_config_path_in_file}'. "
            f"Using defaults: host={chroma_host}, port={chroma_port}"
        )

    # Initialize DatabaseManager (it loads its own config from "database.yaml")
    logging.info("Initializing DatabaseManager...")
    db_manager = DatabaseManager()
    if not db_manager._engine: # Check if engine was initialized by DatabaseManager
        logging.error("DatabaseManager failed to initialize its SQLAlchemy engine. Exiting.")
        return

    logging.info("Initializing SchemaEngineFactory...")
    schema_factory = SchemaEngineFactory() # Instantiate the factory

    logging.info("Initializing SchemaEngine...")
    # Pass the engine from DatabaseManager to the factory's creation method
    schema_engine: SchemaEngine = schema_factory.create_schema_engine(engine=db_manager._engine)

    logging.info("Initializing SentenceTransformerEmbeddingFacade...")
    # This will use the default Qwen model from HuggingFaceModelConstants if not overridden
    embedding_facade = SentenceTransformerEmbeddingFacade()

    logging.info(f"Initializing ChromaClient for host: {chroma_host}, port: {chroma_port}")
    chroma_client = ChromaClient(
        host=chroma_host,
        port=chroma_port,
        embedding_facade=embedding_facade
    )

    collection_name = PreprocessingConstants.COLUMN_COLLECTION_NAME
    logging.info(f"Attempting to get or create ChromaDB collection: {collection_name}")
    # The embedding_function_config is an example; actual ChromaClient might handle this internally
    # or require a different way to specify the model if not using its default.
    # Given the ChromaClient takes embedding_facade, it likely uses it directly.
    collection = chroma_client.get_or_create_collection(
        collection_name=collection_name
        # If your ChromaClient's get_or_create_collection needs embedding function details explicitly:
        # embedding_function_config={"model_name": HuggingFaceModelConstants.DEFAULT_EMBEDDING_MODEL_PATH}
    )
    if not collection:
        logging.error(f"Failed to get or create ChromaDB collection: {collection_name}. Exiting.")
        db_manager.close_connection() # Ensure DB connection is closed on early exit
        return

    logging.info("Fetching table names...")
    try:
        # View support is handled by SchemaEngine's initialization parameters (via factory from schema_engine.yaml)
        table_names: List[str] = schema_engine.get_table_names()

        print('TABLE NAMES', table_names)
    except Exception as e:
        logging.error(f"Failed to fetch table names: {e}")
        db_manager.close_connection()
        return

    if not table_names:
        logging.info("No tables found in the database.")
        db_manager.close_connection()
        return

    documents_to_add: List[str] = []
    metadatas_to_add: List[Dict[str, Any]] = []
    ids_to_add: List[str] = []

    logging.info(f"Processing {len(table_names)} tables...")
    for table_name in table_names:
        logging.info(f"Processing table: {table_name}")
        try:
            # table_comment = schema_engine.get_table_comment(table_name) # Not directly used for column docs
            columns_data: List[Dict[str, Any]] = schema_engine.get_columns(table_name)
        except Exception as e:
            logging.error(f"Failed to get columns for table {table_name}: {e}")
            continue # Skip to next table

        if not columns_data:
            logging.warning(f"No columns found for table: {table_name}")
            continue

        for col_data in columns_data:
            try:
                column_name_val: str = col_data['name']
                column_type_val: str = str(col_data['type']) # Ensure type is string
                column_description_val: str = col_data.get('comment') # Comment might be None

                # Document text is description if available (and not empty/whitespace), otherwise column name
                document_text: str = column_description_val if column_description_val and column_description_val.strip() else column_name_val
                documents_to_add.append(document_text)
                metadatas_to_add.append({
                    "table_name": table_name,
                    "column_name": column_name_val,
                    "column_type": column_type_val
                })
                ids_to_add.append(f"{table_name}_{column_name_val}")
            except KeyError as e:
                logging.error(f"Missing expected key in column data for table {table_name}: {e}. Data: {col_data}")
            except Exception as e:
                logging.error(f"Error processing column {col_data.get('name', 'Unknown')} in table {table_name}: {e}")


    if documents_to_add:
        logging.info(f"Adding/updating {len(documents_to_add)} column documents in ChromaDB collection '{collection_name}'...")
        try:
            chroma_client.add_documents( # ChromaClient's add_documents usually handles add or update via IDs
                collection_name=collection_name,
                documents=documents_to_add,
                metadatas=metadatas_to_add,
                ids=ids_to_add
            )
            logging.info("Successfully added/updated documents in ChromaDB.")
        except Exception as e:
            logging.error(f"Failed to add/update documents in ChromaDB: {e}")
    else:
        logging.info("No new column documents to add or update in ChromaDB.")

    logging.info("Database column preprocessing and ChromaDB population finished.")
    db_manager.close_connection() # Good practice to close DB connection


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate ChromaDB with database column information.")
    parser.add_argument(
        "--chroma_config_file",
        type=str,
        default="chroma_db.yaml",
        help="Name of the ChromaDB configuration file (e.g., chroma_db.yaml) located in the 'config' directory."
    )
    parser.add_argument(
        "--chroma_config_path", # Renamed for clarity
        type=str,
        default="chroma_db", # Default path to chroma settings within its config file
        help="Dot-separated path to the ChromaDB configuration section within its config file (e.g., 'chroma_db')."
    )
    args = parser.parse_args()

    main(chroma_config_file=args.chroma_config_file, chroma_config_path_in_file=args.chroma_config_path)