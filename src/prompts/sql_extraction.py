SQL_EXTRACTION_PROMPT = """
You are an expert SQL parser. Your task is to analyze the provided SQL query and extract all table names, column names, and string literals.

**Instructions:**

1.  **Identify Tables:** List all tables explicitly mentioned in the `FROM` and `JOIN` clauses.
2.  **Identify Columns:** List all column names. If a column is qualified with a table name or alias (e.g., `table.column`), extract just the column name.
3.  **Identify Literals:** Extract all string literals (text enclosed in single quotes).
4.  **Output:** Respond with a JSON object containing three keys: `tables`, `columns`, and `literals`.

**SQL Query:**
{SQL_QUERY}

**JSON Output:**
```json
{{
  "tables": ["table1", "table2", ...],
  "columns": ["column1", "column2", ...],
  "literals": ["literal1", "literal2", ...]
}}
```
"""