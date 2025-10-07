from util.similarity_measures.lsh import LSHUtil

def main():
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

if __name__ == "__main__":
    main()