from util.similarity_measures.bm25 import BM25Util

def main():
    """
    Initializes the RunningManager and starts the evaluation process.
    """
    # load_comments()
    db_id = "california_schools"
    keyword = "Among the schools with the average score in Math over 560 in the SAT test, how many schools are directly charter-funded?"
    bm25_retriever = BM25Util.load_bm25_retriever(db_id)
    
    bm25_results = bm25_retriever.invoke(keyword)
    
    
    # Combine and rerank
    results = []

    for doc in bm25_results:
        results.append({
            "column_name": doc.metadata['column_name'],
            "table_name": doc.metadata['table_name'],
            "description": doc.page_content
        })
    

    print(results)

if __name__ == "__main__":
    main()