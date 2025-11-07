import os
import json
import logging
import chromadb
from chromadb.utils import embedding_functions
from common.config.config_helper import ConfigurationHelper
from components.models.embedding_model_facade import HuggingFaceEmbeddingFacade
from infrastructure.vector_db.chroma_client import ChromaClient
from util.constants import PreprocessingConstants

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(chroma_config_file: str = "chroma_db.yaml", chroma_config_path_in_file: str = "chroma_db"):
    # Load the tokenized questions
    with open("/var/tmp/g62nok/thesis/dataset/train/tokenized_questions.json", "r") as f:
        tokenized_questions = json.load(f)
    cfg_helper = ConfigurationHelper()

    # Configure ChromaDB
    chroma_settings = cfg_helper.get_config(chroma_config_file, chroma_config_path_in_file)
    chroma_host = chroma_settings.get("host", PreprocessingConstants.DEFAULT_CHROMA_HOST)
    chroma_port = int(chroma_settings.get("port", PreprocessingConstants.DEFAULT_CHROMA_PORT))
    
    embedding_facade = HuggingFaceEmbeddingFacade()
    chroma_client = ChromaClient(host=chroma_host, port=chroma_port, embedding_facade=embedding_facade)

    # Create a Chroma collection
    collection_name = "questions_with_sql"
    try:
        chroma_client.get_or_create_collection(collection_name=collection_name)
        #collection = chroma_client.create_collection(name=collection_name)
    except chromadb.db.base.UniqueConstraintError:
        logging.warning(f"Collection {collection_name} already exists. Reusing it.")
        #collection = chroma_client.get_collection(name=collection_name)

    documents_to_add, metadatas_to_add, ids_to_add = [], [], []

    # Insert data into Chroma
    for item in tokenized_questions:
        db_id = item["db_id"]
        original_question = item["original_question"]
        masked_question = item["masked_question"]

        # SQL query (assuming it's available in the item, adjust as needed)

        # Add to Chroma collection
        documents_to_add.append(masked_question)
        metadatas_to_add.append({"db_id": db_id, "sql": item["sql"], "original_question": original_question, "evidence": item["evidence"]})
        ids_to_add.append(f"{db_id}_{original_question}")
        # collection.add(
        #     embeddings=[embedding_facade.embed_queries([masked_question])[0]],  # Embed the masked question
        #     metadatas={"db_id": db_id, "sql_query": sql_query, "original_question": original_question},  # Metadata
        #     ids=[f"{db_id}_{original_question}"]  # Unique ID
        # )
        logging.info(f"Added question: {original_question} to Chroma with db_id: {db_id}")
    chroma_client.add_documents(collection_name=collection_name, documents=documents_to_add, metadatas=metadatas_to_add, ids=ids_to_add)

    logging.info("Data insertion complete.")

if __name__ == "__main__":
    main()