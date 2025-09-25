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
from infrastructure.vector_db.chroma_client import ChromaClient
from common.config.config_helper import ConfigurationHelper
from components.models.embedding_model_facade import HuggingFaceEmbeddingFacade
from util.constants import PreprocessingConstants, DatabaseConstants
from util.db.description_csv import load_database_descriptor
import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3

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
    
    # --- ChromaDB and Embedding Model Setup ---
    chroma_settings = cfg_helper.get_config(chroma_config_file, chroma_config_path_in_file)
    chroma_host = chroma_settings.get("host", PreprocessingConstants.DEFAULT_CHROMA_HOST)
    chroma_port = int(chroma_settings.get("port", PreprocessingConstants.DEFAULT_CHROMA_PORT))
    
    embedding_facade = HuggingFaceEmbeddingFacade()
    chroma_client = ChromaClient(host=chroma_host, port=chroma_port, embedding_facade=embedding_facade)

    db_names = [f.name for f in os.scandir(DatabaseConstants.COLUMN_DESCRIPTIONS) if f.is_dir()]

    for db_name in db_names:
        logging.info(f"Processing database: {db_name}")
        
        database_descriptor = load_database_descriptor(db_name)
        collection_name = f"{PreprocessingConstants.COLUMN_COLLECTION_NAME}_{db_name}"
        
        chroma_client.get_or_create_collection(collection_name=collection_name)

        documents_to_add, metadatas_to_add, ids_to_add = [], [], []
        for table_name, table_descriptor in database_descriptor.tables.items():
            for column_name, column_definition in table_descriptor.columns.items():
                document_text = f"{column_definition.column_description} {column_definition.value_description}".strip()
                if document_text:
                    documents_to_add.append(document_text)
                    metadatas_to_add.append({
                        "table_name": table_name,
                        "column_name": column_name,
                        "column_type": column_definition.data_format
                    })
                    ids_to_add.append(f"{db_name}_{table_name}_{column_name}")

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