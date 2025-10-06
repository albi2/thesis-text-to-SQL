import os
import pickle
import logging
from langchain.retrievers import BM25Retriever
from langchain.docstore.document import Document
from util.db.db_values import get_all_db_ids
from util.db.database_descriptor import DatabaseDescriptor

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to create and save BM25 retrievers for all databases.
    """
    logging.info("Starting BM25 retriever creation for all databases.")
    
    db_ids = get_all_db_ids()
    
    for db_id in db_ids:
        logging.info(f"Processing database: {db_id}")
        
        db_descriptor = DatabaseDescriptor(db_id)
        db_descriptor.get_schema_description()
        
        documents = []
        for table in db_descriptor.tables.values():
            for column in table.columns.values():
                documents.append(Document(
                    page_content=column.description if column.description else column.column_name,
                    metadata={
                        "table_name": table.table_name,
                        "column_name": column.column_name
                    }
                ))
        
        bm25_retriever = BM25Retriever.from_documents(documents)
        
        # Save BM25 retriever
        bm25_path = f"/var/tmp/ge62nok/bm25/{db_id}_bm25_retriever.pkl"
        
        os.makedirs(os.path.dirname(bm25_path), exist_ok=True)
        
        with open(bm25_path, "wb") as f:
            pickle.dump(bm25_retriever, f)
            
        logging.info(f"BM25 retriever saved for database: {db_id}")
        
    logging.info("BM25 retriever creation finished.")

if __name__ == "__main__":
    main()