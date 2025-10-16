
## Running the scripts

```PYTHONPATH=./src python ./scripts/vector_db/populate_column_vectors.py```

## Migrating dbs
```./migration/migrate_db.sh /Users/I746200/Downloads/dev_20240627/dev_databases/california_schools/california_schools.sqlite admin admin govdata thesis localhost 5433```

## Checking SQLs
PYTHONPATH=./src python scripts/analysis/check_sql_comparison.py --results_path=../results/evaluation_results_16_nosmallmodels_geminigen_refinement_criteriagen_improvedkeywordprompt.json --questions_path=./dataset/dev/bird_subset.json