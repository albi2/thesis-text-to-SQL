PROMPT = """
You are a SQLite expert. Your task is to correct an incorrect SQL query based on the provided database schema, the user's question, and the error message from the database.

**Database Schema:**
{DATABASE_SCHEMA}

**User's Question:**
{QUESTION}

**Incorrect SQL Query:**
{SQL_QUERY}

**Execution Error:**
{ERROR_MESSAGE}

Output format:
In your answer, please enclose the generated SQL query in a code block:
```sql
-- Your SQL query
```
"""