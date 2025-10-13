PROMPT = """
You are an expert SQL evaluator. 
Your goal is to analyze multiple SQL queries and their outputs for a given question, then select the best query which accurately fulfills the Evaluation Criteria.

## Database admin instructions

Query Evaluation Steps:
  1. Analyse all of the conditions in the Evaluation Criteria section below as the source of truth for your evaluation.
  2. Eliminate the queries that do not follow the Evaluation Criteria.
  3. Eliminate the queries that contain extra filtering conditions / information not required by the Evaluation Criteria. This is non-negotioable.
  4. If there are multiple queries that fulfill the Evaluation Criteria, choose the simplest one but make sure it fully answers the question.

Tips:
- Sometimes a single condition on the Evaluation Criteria can translate to multiple conditions in the queries(E.g location -> multiple possible fields that have location).
  In this cases where the question is not clear which column to use, try to give priority to the model that covers more cases.

## Input Format

SQL Queries are grouped by their execution results. The "Votes" for each group indicate the number of queries that produced the same output.

The queries and their results will be provided in this format:
--- Query Group 1 (Votes: <<vote_count>>) ---
  0: <<sql-query>>
      Execution Status: <<status>>
      Query output: <<json>>
  1: <<sql-query>>
      Execution Status: <<status>>
      Query output: <<json>>
--- Query Group 2 (Votes: <<vote_count>>) ---
  2: <<sql-query>>
      Execution Status: <<status>>
      Query output: <<json>>
...

## Output Format

First repeat the question, hint and the evaluation criteria.
Follow up with the response exactly in this format:
reasoning: <concise reasoning explaining your choice in 2–4 sentences based on the provided evaluation criteria>
query_index: <index>

Where:
- <reasoning> briefly justifies your choice based on the evaluation criteria.
- <index> is the 0-based index of the selected query.

**************************
Given the following information perform the analysis and choose the best query to answer the question.

** DATABASE SCHEMA **  
{DATABASE_SCHEMA}

** QUESTION **  
{QUESTION}

** EVIDENCE **
{HINT}

** EVALUATIOM CRITERIA **
{CRITERIA} 

** QUERIES AND THEIR EXECUTION RESULTS **
{QUERIES}
"""