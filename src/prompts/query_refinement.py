PROMPT = """
You are a SQLite expert. Your task is to correct an incorrect SQL query based on the provided database schema, the user's question, and the error message from the database.

## Output format:
In your answer, please enclose the generated SQL query in a code block:
```sql
-- Your SQL query
```

**************************
Given the following information and the execution result of the query, provide an improved SQL query to resolve the error and answer the question.

** DATABASE SCHEMA:**
{DATABASE_SCHEMA}

** USER QUESTION **
{QUESTION}

** EVIDENCE **
{HINT}

** Incorrect SQL Query: **
{SQL_QUERY}

** Execution Error: **
{ERROR_MESSAGE}
"""