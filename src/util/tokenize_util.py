import os
import pickle
import logging
from datasketch import MinHashLSH
from util.similarity_measures.lsh import LSHUtil
from util.similarity_measures.edit import EditDistanceUtil
from src.pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever
import re

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def tokenize_question(question, table, information_retriever, db_id):
    # Replace table and column names with [MASK] and literals with [UNK]
    masked_question = question

    lsh_path = f"/var/tmp/ge62nok/lsh/train/{db_id}_lsh.pkl"
    minhashes_path = f"/var/tmp/ge62nok/lsh/train/{db_id}_minhashes.pkl"

    try:
        with open(lsh_path, "rb") as f:
            lsh = pickle.load(f)
        with open(minhashes_path, "rb") as f:
            minhashes = pickle.load(f)
    except FileNotFoundError:
        lsh = None
        minhashes = None

    # Replace anything in any kind of quotes with [UNK]
    masked_question = re.sub(r'["\']([^"\']*)["\']', "[UNK]", masked_question)

    # Replace table names (case-insensitive)
    for table_name in table["table_names"]:
        masked_question = re.sub(r'\b' + re.escape(table_name) + r'\b', "[MASK]", masked_question, flags=re.IGNORECASE)

    # Replace column names (case-insensitive)
    for column in table["column_names"]:
        if column[1] != "*":
            masked_question = re.sub(r'\b' + re.escape(column[1]) + r'\b', "[MASK]", masked_question, flags=re.IGNORECASE)

    # Find literals using LSH and edit distance
    if lsh is not None and minhashes is not None:
        question_tokens = masked_question.split()
        token_list = []
        for n in range(1, min(4, len(question_tokens) + 1)):
            for i in range(len(question_tokens) - n + 1):
                token_tuple = question_tokens[i:i+n]
                token_list.append(" ".join(token_tuple))
        candidates = []
        for phrase in token_list:
            similar_values = LSHUtil.query_lsh(lsh, minhashes, phrase, 100)
            for table_name, columns in similar_values.items():
                for column_name, values in columns.items():
                    for value in values:
                        candidates.append({"value": value, "table_name": table_name, "column_name": column_name, "token": token})

            filtered_candidates = EditDistanceUtil.get_similar_by_threshold(phrase, candidates, threshold=0.95)
            if len(filtered_candidates) > 1:
                masked_question = masked_question.replace(phrase, "[UNK]")

    # Extract entities using GLiNER
    entities = information_retriever.extract_entities_with_gliner(question)
    for entity in entities:
        masked_question = re.sub(r'\b' + re.escape(entity) + r'\b', "[UNK]", masked_question, flags=re.IGNORECASE)

