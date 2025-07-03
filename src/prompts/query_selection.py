PROMPT = """ 
You are an expert in analyzing SQL queries and determining their relevance to agiven question. 
Your task is to evaluate multiple SQL queries and select the one that best answers the question based on the provided database schema and context.
## Responsibilities
1. Analyze the given question: Understand the intent of the question and its expected output. 
2. Evaluate each SQL query: Consider the correctness, relevance, and completeness of each query in relation to the question. 
3. Select the best query: Choose the query that most accurately answers the question, while considering database structure, table relationships,
 and query efficiency.
## Requirements 
- Respond with the most relevant SQL query, and nothing else. 
- Ensure the selected query is valid for the given database schema and directly
addresses the question. 

You are given a question, a database schema, multiple SQL queries, and their execution results. 
Your task is to select the SQL query that best answers the question based on the query and its result.

## Instructions 
1. Understand the Question: Determine what the user is asking and identify the specific information that needs to be retrieved. 
2. Evaluate Each Query and Response Pair: For each provided SQL query and its result, determine: - Query Accuracy: Does the query correctly represent the user's intent? - Result Relevance: Does the result contain the data needed to answer the question completely and correctly? - Efficiency: Is the query optimized, avoiding unnecessary complexity?
3. The queries will be provided in the format:
    0: Query 1
       Query output: <<json>>
    1: Query 2
       Query output: <<json>>
    ...
   Answer with the format: ```query_index: <index>```, where `<index>` is the index of the query that best answers the question.

## Database Schema Database:
{DATABASE_SCHEMA}

## Question 
{QUESTION}

## Hint 
{HINT}

## SQL Queries and Execution Results 
{QUERIES}
"""


QUERY_SELECTION_PROMPT = """ You are given a question, a database schema, and multiple SQL queries. Your task
is to select the SQL query that is most relevant and best answers the question.
## Instructions 1. Analyze the Question: Understand what the user is asking and identify the
information that needs to be extracted from the database. 2. Evaluate SQL Queries: For each provided SQL query, determine its relevance
based on: - Accuracy: Does the query correctly match the question's intent? - Completeness: Does the query retrieve all the necessary information without omitting important details?
- Efficiency: Is the query optimized for the task, avoiding unnecessary joins or conditions?
3. Select the Most Relevant Query: Choose the query that is the best match for the question.
## Database Schema Database "{database_name}": {database_schema}
## Question The question is: {question}
## Hint {hint}
## SQL Queries {queries}
## Output Requirement Reply the query Index in the format of "Index: ".
## Output """
query_with_response_selection_prompt = """ You are given a question, a database schema, multiple SQL queries, and their
execution results. Your task is to select the SQL query that best answers the question based on the query and its result.
## Instructions 1. Understand the Question: Determine what the user is asking and identify the
specific information that needs to be retrieved. 2. Evaluate Each Query and Response Pair: For each provided SQL query and its
result, determine: - Query Accuracy: Does the query correctly represent the user's intent? - Result Relevance: Does the result contain the data needed to answer the question completely and correctly? - Efficiency: Is the query optimized, avoiding unnecessary complexity?
## Database Schema Database "{database_name}": {database_schema}
## Question {question}
## Hint {hint}
## SQL Queries and Execution Results {queries}
## Output Requirement Only reply the query Index in the format of "Index: ". """