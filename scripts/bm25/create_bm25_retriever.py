import os
import pickle
import logging
from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from util.constants import DatabaseConstants
from util.db.description_csv import load_database_descriptor

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to create and save BM25 retrievers for all databases.
    """
    logging.info("Starting BM25 retriever creation for all databases.")
    
    db_names = [f.name for f in os.scandir(DatabaseConstants.COLUMN_DESCRIPTIONS) if f.is_dir()]
    
    for db_name in db_names:
        logging.info(f"Processing database: {db_name}")
        
        database_descriptor = load_database_descriptor(db_name)
        
        documents = []
        for table_name, table_descriptor in database_descriptor.tables.items():
            for column_name, column_definition in table_descriptor.columns.items():
                # Add column name as a document
                documents.append(Document(
                    page_content=column_definition.column_name,
                    metadata={
                        "table_name": table_name,
                        "column_name": column_name,
                        "type": "column_name"
                    }
                ))

                # Add column description as a document if it exists
                if column_definition.column_description:
                    documents.append(Document(
                        page_content=column_definition.column_description,
                        metadata={
                            "table_name": table_name,
                            "column_name": column_name,
                            "type": "column_description"
                        }
                    ))

                # Add value description as a document if it exists
                if column_definition.value_description:
                    documents.append(Document(
                        page_content=column_definition.value_description,
                        metadata={
                            "table_name": table_name,
                            "column_name": column_name,
                            "type": "value_description"
                        }
                    ))
        
        bm25_retriever = BM25Retriever.from_documents(documents, k=20)
        
        # Save BM25 retriever
        bm25_path = f"/var/tmp/ge62nok/bm25/{db_name}_bm25_retriever.pkl"
        
        os.makedirs(os.path.dirname(bm25_path), exist_ok=True)
        
        with open(bm25_path, "wb") as f:
            pickle.dump(bm25_retriever, f)
            
        logging.info(f"BM25 retriever saved for database: {db_name}")
        
    logging.info("BM25 retriever creation finished.")

if __name__ == "__main__":
    main()