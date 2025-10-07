from util.similarity_measures.lsh import LSHUtil
from util.similarity_measures.bm25 import BM25Util
from pipeline.steps.information_retrieval.executor.information_retrieval import InformationRetriever

def test_bm25():
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

def test_lsh():
    """
    Initializes the RunningManager and starts the evaluation process.
    """
    # load_comments()
    db_id = "california_schools"
    keyword = "Los Angeles"
    lsh = LSHUtil.load_lsh_index(db_id)
    minhashes = LSHUtil.load_minhashes(db_id)
    
    similar_values = LSHUtil.query_lsh(lsh, minhashes, keyword)
    
    filtered_minhashes = {key: value for key, value in minhashes.items() if value["column_name"] == 'City'}
    column_names = set([value["column_name"] for key,value in minhashes.items()])
    print(column_names)

def main():
    information_retrieve = InformationRetriever()
    


if __name__ == "__main__":
    main()