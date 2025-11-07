import os
import pickle
import logging
from datasketch import MinHashLSH
from util.db.db_values import get_unique_values_for_db_with_path
from util.similarity_measures.lsh import LSHUtil
from util.constants import DatabaseConstants, LSHConstants
import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3
import json
from infrastructure.database.database_manager import DatabaseManager

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to create and save LSH indexes and MinHash mappings for all databases.
    """
    logging.info("Starting LSH index creation for all databases.")

    # Load train_tables.json
    with open("var/tmp/ge62nok/thesis/dataset/train/train_tables.json", "r") as f:
        train_tables = json.load(f)

    for table_data in train_tables:
        db_id = table_data["db_id"]

        logging.info(f"Processing database: {db_id}")

        # Get unique values using the existing function
        unique_values = get_unique_values_for_db_with_path(db_id, DatabaseConstants.SQLITE_TRAIN_PATH)

        lsh = MinHashLSH(threshold=LSHConstants.DEFAULT_THRESHOLD, num_perm=LSHConstants.DEFAULT_NUM_PERM)
        minhashes = {}

        for table_name, columns in unique_values.items():
            print(f"Initial unique values for table {table_name} , column {columns.keys()}: {list(columns.keys())[:5]}")
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
        lsh_path = f"/var/tmp/ge62nok/lsh/train/{db_id}_lsh.pkl"
        minhashes_path = f"/var/tmp/ge62nok/lsh/train/{db_id}_minhashes.pkl"

        os.makedirs(os.path.dirname(lsh_path), exist_ok=True)

        with open(lsh_path, "wb") as f:
            pickle.dump(lsh, f)

        with open(minhashes_path, "wb") as f:
            pickle.dump(minhashes, f)

        logging.info(f"LSH index and MinHash mappings saved for database: {db_id}")

    logging.info("LSH index creation finished.")

if __name__ == "__main__":
    main()