from util.similarity_measures.lsh import LSHUtil
from util.similarity_measures.bm25 import BM25Util
from pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever
from executor.task_model import Task
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
    db_id = "student_club"
    keyword = "Sacha Harrison"
    lsh = LSHUtil.load_lsh_index(db_id)
    minhashes = LSHUtil.load_minhashes(db_id)
    
    similar_values = LSHUtil.query_lsh(lsh, minhashes, keyword)
    
    filtered_minhashes = {key: value for key, value in minhashes.items() if value["column_name"] == 'City'}
    column_names = set([value["column_name"] for key,value in minhashes.items()])
    print(similar_values)

def main():
    information_retriever = InformationRetriever()
    keywords = ["grade"]
    task = Task(question_id="1", db_id="california_schools", question="In which city can you find the school in the state of California with the lowest latitude coordinates and what is its lowest grade? Indicate the school name.")
    # retrieved_schema = information_retriever.retrieve_context(keywords, task)
    retrieved_entities = information_retriever.retrieve_entities(db_id="student_club", phrases=["Sacha Harrison"])
    print(f"RETRIEVED SCHEMA : {retrieved_entities}")
    # test_lsh()

if __name__ == "__main__":
    main()