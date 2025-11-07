import os
import pickle
import logging
import json
import re
import sys
sys.modules["sqlite3"] = sys.modules.get("sqlite3", None)
from util.tokenize_util import tokenize_question
from pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    # Load the training data
    with open("/var/tmp/ge62nok/thesis/dataset/train/train.json", "r") as f:
        train_data = json.load(f)

    # Load the table schemas
    with open("/var/tmp/ge62nok/thesis/dataset/train/train_tables.json", "r") as f:
        train_tables = json.load(f)

    # Create a dictionary mapping db_id to table schema
    table_schemas = {table["db_id"]: table for table in train_tables}

    # Tokenize the questions
    for item in train_data:
        db_id = item["db_id"]
        question = item["question"]

        # Get the table schema for the current database
        table = table_schemas.get(db_id)
        if table is None:
            print(f"Table schema not found for db_id: {db_id}")
            continue

        # Tokenize the question
        information_retriever = InformationRetriever()
        masked_question = tokenize_question(question, table, information_retriever, db_id)
        print(f"Original question: {question}")
        print(f"Masked question: {masked_question}")
        print("-" * 20)


if __name__ == "__main__":
    main()