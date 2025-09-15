import os
import pickle
import logging
from datasketch import MinHashLSH
from util.db.db_values import get_all_db_ids, get_unique_values_for_db
from util.similarity_measures.lsh import LSHUtil
from util.constants import LSHConstants

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to create and save LSH indexes and MinHash mappings for all databases.
    """
    logging.info("Starting LSH index creation for all databases.")
    
    db_ids = get_all_db_ids()
    
    for db_id in db_ids:
        logging.info(f"Processing database: {db_id}")
        
        unique_values = get_unique_values_for_db(db_id)
        
        lsh = MinHashLSH(threshold=LSHConstants.DEFAULT_THRESHOLD, num_perm=LSHConstants.DEFAULT_NUM_PERM)
        minhashes = {}
        
        for table_name, columns in unique_values.items():
            for column_name, values in columns.items():
                for i, value in enumerate(values):
                    minhash = LSHUtil.create_minhash(value, num_perm=LSHConstants.DEFAULT_NUM_PERM, n_gram_size=LSHConstants.DEFAULT_N_GRAM_SIZE)
                    key = f"{table_name}_{column_name}_{i}"
                    lsh.insert(key, minhash)
                    minhashes[key] = {
                        "table_name": table_name,
                        "column_name": column_name,
                        "value": value,
                        "minhash": minhash
                    }
        
        # Save LSH index and MinHash mappings
        lsh_path = f"/root/thesis/dataset/lsh/{db_id}_lsh.pkl"
        minhashes_path = f"/root/thesis/dataset/lsh/{db_id}_minhashes.pkl"
        
        os.makedirs(os.path.dirname(lsh_path), exist_ok=True)
        
        with open(lsh_path, "wb") as f:
            pickle.dump(lsh, f)
            
        with open(minhashes_path, "wb") as f:
            pickle.dump(minhashes, f)
            
        logging.info(f"LSH index and MinHash mappings saved for database: {db_id}")
        
    logging.info("LSH index creation finished.")

if __name__ == "__main__":
    main()