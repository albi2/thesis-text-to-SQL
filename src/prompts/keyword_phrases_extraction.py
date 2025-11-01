FEW_SHOT_EXAMPLES_FOR_DICT_OUTPUT_STR = """
Example 1:
Question: "Show me all customers from Germany who ordered iPhone 14 Pro"
Hint: "Focus on location, customer entity, and specific product mentions."
Output:
```json
{"keywords": ["customers", "location", "product"], "phrases": ["Germany", "iPhone 14 Pro"]}
```

Example 2:
Question: "List the top 5 employees by salary in the Sales department"
Hint: "Consider job roles, compensation, and organizational units."
Output:
```json
{"keywords": ["employees", "salary", "department", "job", "compensation", "organizational"], "phrases": ["Sales"]}
```

Example 3:
Question: "What are the most common issues reported for the 'Alpha' project last quarter?"
Hint: "Identify the project name, timeframe, and the type of information requested (issues)."
Output:
```json
{"keywords": ["issues", "project", "quarter", "name", "time"], "phrases": ["Alpha"]}
```

Example 4:
Question: "Show me pending invoices for Microsoft exceeding $10,000"
Hint: "Look for status indicators, company names, and monetary thresholds."
Output:
```json
{"keywords": ["invoices", "status", "amount", "company", "name", "monetary"], "phrases": ["pending", "Microsoft"]}
```

Example 5:
Question: "Get all support tickets created by email domain @acme.com with priority high"
Hint: "Identify the data type, filtering criteria including patterns and severity levels."
Output:
```json
{"keywords": ["tickets", "support", "email", "domain", "priority", "severity"], "phrases": ["@acme.com", "high"]}
```

Example 6:
Question: "List active subscriptions expiring in March 2025"
Hint: "Focus on status, lifecycle events, and date ranges."
Output:
```json
{"keywords": ["subscriptions", "status", "expiration", "date"], "phrases": ["active", "March 2025"]}
```

Example 7:
Question: "Find transactions tagged as 'Refund' processed by user admin_sarah"
Hint: "Identify transaction types, labels/tags, and user identifiers."
Output:
```json
{"keywords": ["transactions", "tags", "user", "labels", "user"], "phrases": ["Refund", "admin_sarah"]}
```

Example 8:
Question: "Get all Toyota Camry vehicles sold in January with mileage under 30000"
Hint: "Consider vehicle make/model, time period, and condition metrics."
Output:
```json
{"keywords": ["vehicles", "model", "mileage", "month", "time", "condition"], "phrases": ["Toyota Camry", "January"]}
```

Example 9:
Question: "Which suppliers from Japan have contract value greater than 500000 yen?"
Hint: "Look at supplier location, contract metrics, and currency amounts."
Output:
```json
{"keywords": ["suppliers", "location", "contract", "currency"], "phrases": ["Japan", "yen"]}
```
"""

PROMPT = """
You are a linguistics expert specializing in information extraction.
Your task is to analyze the given question and hint, then extract keywords and phrases.

## What to Extract

**Keywords** - Nouns that represent things, properties, or measurements:
- Things/entities (e.g., "customers", "orders", "employees", "products")
- Properties (e.g., "salary", "status", "location", "date")
- Measurements (e.g., "count", "total", "average")
- General concepts (e.g., "revenue", "performance", "delivery")
- ❌ DO NOT include verbs or actions

**Phrases** - Specific real-world values:
- Names (e.g., "SAP", "Henry Cavill", "Toronto")
- Specific text / Entity values(e.g., "jimmyneutron231", "GHK", "23 January 2023")
- Status words (e.g., "pending", "active", "failed", "in transit")
- Categories (e.g., "high priority", "sales department", "refund")
- ❌ DO NOT include words like "below", "more than", "greater than"
- ❌ DO NOT include vague descriptions
- ⚠️ If there are no specific values in the question, leave phrases EMPTY

## How to Extract

1. **Read the question** - What is it asking about? What specific details does it mention?
2. **Read the hint** - What additional information does it provide?
3. **Find keywords** - Look for nouns that describe what the question is about
4. **Find phrases** - Look for specific values, names, or concrete examples
5. **Combine everything** - Put all keywords and phrases together, removing duplicates

## Rules

- Only extract words that actually appear in the question or hint
- Don't make up or guess at words
- Keep the original wording - don't paraphrase
- Skip verbs and action words

## Output Format

Return ONLY this JSON structure:
```json
{{
  "keywords": ["keyword1", "keyword2", ...],
  "phrases": ["phrase1", "phrase2", ...]
}}
```

No other text or explanation.

## Examples
{FEWSHOT_EXAMPLES}

**************************

## Your Task

Extract keywords and phrases from the question and hint below.

**USER QUESTION**
{QUESTION}

**EVIDENCE**
{HINT}
"""