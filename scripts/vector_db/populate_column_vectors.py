"""
Script to preprocess database column information and populate a ChromaDB collection.

This script connects to a database, extracts schema information (tables and columns),
and then stores representations of these columns (name or description) into
a ChromaDB vector store. This allows for semantic searching of database columns.
"""
import os
os.environ['PYTORCH_NVML_BASED_CUDA_CHECK'] = "1"

import logging
import argparse
from typing import List, Dict, Any
import sys
import torch
from sqlalchemy import create_engine, text

from infrastructure.vector_db.chroma_client import ChromaClient
from infrastructure.database.database_manager import DatabaseManager
from components.schema.schema_engine import SchemaEngine
from components.schema.schema_engine_factory import SchemaEngineFactory
from common.config.config_helper import ConfigurationHelper
from components.models.embedding_model_facade import HuggingFaceEmbeddingFacade
from util.constants import PreprocessingConstants, DatabaseConfigKeys

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# if torch.cuda.is_available():
#     torch.cuda.empty_cache()
#     print("CUDA cache emptied.")

os.environ['CHROMA_TELEMETRY_ANALYTICS'] = 'False'

def main(chroma_config_file: str = "chroma_db.yaml", chroma_config_path_in_file: str = "chroma_db") -> None:
    """
    Main function to extract database column information and populate ChromaDB.

    Args:
        chroma_config_file (str, optional): Name of the ChromaDB configuration file.
        chroma_config_path_in_file (str, optional): Path within the ChromaDB config file to its settings.
    """
    os.environ['PYTORCH_NVML_BASED_CUDA_CHECK'] = "1"
    logging.info("Starting database column preprocessing for ChromaDB population.")

    cfg_helper = ConfigurationHelper()
    db_config = cfg_helper.get_config("database.yaml", "database")
    
    # --- Database Connection Setup ---
    host = db_config.get(DatabaseConfigKeys.HOST)
    port = db_config.get(DatabaseConfigKeys.PORT)
    user = db_config.get(DatabaseConfigKeys.USERNAME)
    password = db_config.get(DatabaseConfigKeys.PASSWORD)
    db_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(db_url)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        db_names = [row[0] for row in result]

    # --- ChromaDB and Embedding Model Setup ---
    chroma_settings = cfg_helper.get_config(chroma_config_file, chroma_config_path_in_file)
    chroma_host = chroma_settings.get("host", PreprocessingConstants.DEFAULT_CHROMA_HOST)
    chroma_port = int(chroma_settings.get("port", PreprocessingConstants.DEFAULT_CHROMA_PORT))
    
    embedding_facade = HuggingFaceEmbeddingFacade()
    chroma_client = ChromaClient(host=chroma_host, port=chroma_port, embedding_facade=embedding_facade)
    schema_factory = SchemaEngineFactory()

    for db_name in db_names:
        if db_name in ["govdata", "postgres"]:
            continue

        logging.info(f"Processing database: {db_name}")
        
        db_manager = DatabaseManager()
        db_engine = db_manager.create_engine(db_name)

        schema_engine: SchemaEngine = schema_factory.create_schema_engine(engine=db_engine, db_name=db_name)
        collection_name = f"{PreprocessingConstants.COLUMN_COLLECTION_NAME}_{db_name}"
        
        chroma_client.get_or_create_collection(collection_name=collection_name)

        try:
            table_names: List[str] = schema_engine.get_table_names()
        except Exception as e:
            logging.error(f"Failed to fetch table names for {db_name}: {e}")
            db_manager.close_connections(db_engine)
            continue

        if not table_names:
            logging.info(f"No tables found in database {db_name}.")
            db_manager.close_connections(db_engine)
            continue

        documents_to_add, metadatas_to_add, ids_to_add = [], [], []
        for table_name in table_names:
            try:
                columns_data: List[Dict[str, Any]] = schema_engine.get_columns(table_name)
            except Exception as e:
                logging.error(f"Failed to get columns for table {table_name} in {db_name}: {e}")
                continue

            for col_data in columns_data:
                comment = col_data.get('comment')
                document_text = comment.strip() if comment else col_data['name']
                documents_to_add.append(document_text)
                metadatas_to_add.append({
                    "table_name": table_name,
                    "column_name": col_data['name'],
                    "column_type": str(col_data['type'])
                })
                ids_to_add.append(f"{db_name}_{table_name}_{col_data['name']}")

        if documents_to_add:
            try:
                chroma_client.add_documents(
                    collection_name=collection_name,
                    documents=documents_to_add,
                    metadatas=metadatas_to_add,
                    ids=ids_to_add
                )
                logging.info(f"Successfully added/updated documents in ChromaDB for {db_name}.")
            except Exception as e:
                logging.error(f"Failed to add/update documents in ChromaDB for {db_name}: {e}")
        
        db_manager.close_connections(db_engine)

    logging.info("Database column preprocessing and ChromaDB population finished.")


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