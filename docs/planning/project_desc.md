# Project Plan: Small Model Text-to-SQL Framework

This plan outlines the setup, modular components, and evaluation strategy for a Python-based Text-to-SQL framework using 7B parameter models. The focus is on modularity, diverse candidate generation, and iterative refinement, with an emphasis on research and testing various approaches.

---

## Phase 1: Project Setup & Foundational Research

1.  **Environment Setup**
    * Initialize Python project with virtual environment.
    * Install necessary libraries: `transformers`, `torch` (or `tensorflow`), `langchain`, `sqlparse`, database connectors (e.g., `psycopg2`, `sqlite3`), `pandas`, `numpy`, `scikit-learn`.
    * Set up a local test database (e.g., PostgreSQL, SQLite) with sample data from BIRD/Spider datasets.
    * Implement basic logging and configuration management.

2.  **Model Selection & Preparation**
    * **Text-to-SQL Models (7B parameters):**
        * **Exploration:** Evaluate pre-trained/fine-tuned models like Mistral 7B, Llama2 7B, Gemma 7B, DeciLM 7B (especially those fine-tuned on SQL Create Context or similar datasets).
        * **Action:** Select 1-2 promising models for initial experimentation. Investigate their specific licensing and deployment requirements.
    * **Reasoning Models (7B parameters):**
        * **Exploration:** Investigate MiMo-7B and Phi-4-reasoning for their strong mathematical and code reasoning capabilities.
        * **Action:** Select 1-2 models to use for components requiring complex reasoning (e.g., decomposition, error analysis, self-refinement).
    * **Model Loading:** Develop modular code for loading selected models into memory (or using HuggingFace `pipeline` for inference).

3.  **Core Utilities**
    * **Database Connector:** Abstract database connection, schema introspection, and query execution functionalities.
    * **Schema Loader:** Develop utilities to load database schemas into various formats (e.g., plain text, JSON, `CREATE TABLE` statements).
    * **Dataset Handling:** Prepare utilities for loading and processing the BIRD/Spider datasets, including schema and question parsing.

---

## Phase 2: Modular Component Development & Exploration

#### Component 1: Database Tables Pruning & Schema Presentation

* **Objective:** Select relevant tables and present schema efficiently to the LLM.
* **Schema Presentation Formats Exploration:**
    * **Plain Text/Concatenated DDL:** Full `CREATE TABLE` statements (as in Spider, BIRD).
    * **JSON Format:** Structured representation including table names, column names, data types, primary keys (PKs), foreign keys (FKs) with explicit linking, and natural language descriptions.
    * **Semi-structured (M-Schema):** Explore hierarchical representation including schema elements, descriptions, and examples (from XiYan-SQL).
    * **FK Encoding:** Experiment with explicit notation of foreign key relationships within the chosen schema format (e.g., `FOREIGN KEY (column_name) REFERENCES table_name(pk_column)` or a dedicated section listing relationships).
    * **Sample Data:** Experiment with including a few rows of sample data per table (e.g., from ACT-SQL).
* **Table Pruning Techniques Exploration:**
    * **Semantic Similarity:** Use embeddings (e.g., Sentence Transformers) to match question terms with table/column names/descriptions.
    * **DFIN-SQL "Focused Schema":** Implement RAG-like retrieval of relevant schema subsets using prompt-based techniques.
    * **Graph-based Pruning:** Explore representing schema as a graph and using graph algorithms (e.g., shortest path between entities) for relevance.
    * **LLM-based Pruning (Selector Agent):** Use a small reasoning LLM (or a fine-tuned 7B model) to identify relevant tables based on question and full schema.
* **Action:** Implement at least 2-3 combinations of schema presentation and pruning techniques for comparative testing.

#### Component 2: Relevant Columns Linking

* **Objective:** Select relevant columns from chosen tables, minimizing token usage.
* **Column Linking Techniques Exploration:**
    * **Semantic Similarity:** Similar to table pruning, apply embedding-based matching between question and column names/descriptions.
    * **LLM-based Filtering:** Provide the LLM with relevant tables and prompt it to select the most relevant columns, considering data types and context.
    * **DFIN-SQL & MAC-SQL Inspired:** Adapt their strategies for prompt-based column selection, potentially guided by the question and table context.
    * **Heuristic-based:** Consider rules like always including primary keys, or columns with common entity names.
* **Action:** Integrate column linking with table pruning. Test strategies that prioritize recall (initial over-selection) to avoid missing critical columns.

#### Component 3: Multi-Path Generation

* **Objective:** Generate diverse candidate SQL queries to maximize the chance of a correct one.
* **Generation Strategies Exploration (using Text-to-SQL 7B models):**
    * **Direct Generation:** Standard zero-shot or few-shot prompting.
    * **Chain-of-Thought (CoT):** Prompt the LLM to generate intermediate reasoning steps before the SQL query (e.g., logical plan, steps for decomposition).
    * **Query Decomposition (MAC-SQL, DTS-SQL inspired):**
        * Use a reasoning LLM to decompose complex NL questions into simpler sub-questions.
        * Generate SQL for each sub-question.
        * Combine sub-query results (e.g., using `JOIN`, `UNION`, subqueries, or LLM-based merging).
    * **Constraint-based Generation:** Explore techniques like "LogicalBeam" which use constrained infilling or dynamic schema/grammar constraints (potentially integrating CFGs).
    * **Ensemble Generation (XiYan-SQL inspired):**
        * Combine different prompting strategies (e.g., CoT vs. direct, different few-shot examples).
        * Vary beam search parameters (e.g., beam width, temperature/top-k/top-p) to encourage diversity.
        * Experiment with selective avoidance of pruning/linking in some generation paths to test their impact on complex queries.
* **Action:** Implement at least 3-4 distinct generation paths/strategies. For each path, generate multiple candidates using beam search (e.g., beam width of 3-5).

#### Component 4: Validator

* **Objective:** Ensure generated SQL queries are syntactically and semantically executable.
* **Validation Techniques Exploration:**
    * **Syntactic Validation:** Use `sqlparse` or similar libraries to check for basic syntax errors.
    * **Database Execution:** Attempt to execute the query against the target database (or a dummy/schema-only database). Catch exceptions (syntax errors, invalid column/table names, logical errors).
    * **Unification-based DCGs (CFGs):** Investigate integrating a Python-based library for definite clause grammars to *guarantee* syntactic and schema-faithful validity *before* execution. This acts as a powerful pre-check.
    * **LLM Self-Correction (ReFoRCE, DART-SQL inspired):**
        * Provide the LLM with the failed query and the error message/stack trace.
        * Prompt the LLM to identify and correct the error, then regenerate the query.
* **Retry Mechanism Exploration:**
    * **Error Categorization:** Categorize SQL errors (syntax, schema, logical, execution).
    * **Targeted Retries:** Based on error category, inform the LLM or apply specific correction logic.
    * **Parameterization:** Define parameters for maximum number of retries (e.g., 1-3) and retry strategy (e.g., simple retry, informed retry with error message).
* **Action:** Implement a multi-stage validator: syntactic check, then DCG check (if feasible), then execution with error handling and LLM-based self-correction/retries.

#### Component 5: Reranker

* **Objective:** Select the best SQL query among the generated candidates.
* **Reranking Criteria Exploration:**
    * **Execution Success:** Prioritize queries that execute without error.
    * **Execution Results Consistency:** Compare results of candidates against a known semantic understanding (challenging for open-ended questions, but useful for test cases).
    * **LLM-based Evaluation (Confidence):** Use a reasoning LLM to assess the semantic correctness/relevance of the generated SQL relative to the natural language question, potentially assigning a confidence score.
    * **Test Case Pass Rates:** For benchmark datasets (or synthetic test cases), evaluate candidates by executing them against generated test cases and counting passes.
    * **Semantic Similarity (NL-SQL):** Use cross-encoders or bi-encoders to measure semantic similarity between the original NL question and the generated SQL (or its derived meaning/result).
    * **Query Complexity/Simplicity:** Prefer simpler queries if they achieve the same result.
* **Reranking Methods Exploration:**
    * **Rule-based:** Prioritize based on a hierarchy of criteria (e.g., executable > non-executable, then highest LLM score).
    * **Fine-tuned Selection Model (XiYan-SQL inspired):** Train a small classification model (could be a smaller 7B model fine-tuned for comparison) to select the best query based on features like LLM confidence, execution status, syntax correctness, etc.
    * **Reciprocal Rank Fusion (RRF):** Combine scores from multiple reranking criteria.
* **Action:** Implement a multi-criteria reranker. Prioritize execution success. Test at least 2-3 different combinations of criteria and weighting.

#### Component 6 (Optional): Refiner

* **Objective:** Improve the top-k selected queries for edge cases or further optimization.
* **Refinement Strategies Exploration:**
    * **Execution-Guided Refinement (DART-SQL, MAC-SQL inspired):** If the reranker identifies a query as "best" but it still has subtle issues (e.g., incorrect aggregation, missing `ORDER BY`), provide execution results or a semantic error hint to the LLM for targeted refinement.
    * **Query Rewriting/Optimization:** Prompt the LLM to optimize the query for performance or readability (e.g., convert subqueries to joins where appropriate).
    * **User Feedback Loop:** Design the optional step to integrate future user feedback for refinement (if integrated into a chat LLM).
* **Action:** If time and resources permit, implement a simple refiner component that takes the top 1-2 queries and attempts one round of LLM-based refinement based on specific rules or feedback.

---

## Phase 3: Evaluation & Iteration

1.  **Dataset Preparation:**
    * **Custom Dataset:** Create a small, representative custom dataset of NL questions and corresponding ground truth SQL queries (and potentially results) that reflect your specific use case. This is crucial for initial rapid iteration.
    * **Public Benchmarks:** Set up evaluation on subsets of BIRD / Spider datasets to align with common text-to-SQL benchmarks.
2.  **Evaluation Metrics:**
    * **Execution Accuracy:** The primary metric: percentage of generated queries that execute correctly and produce the same result as the ground truth.
    * **Exact Match Accuracy (for Spider):** Percentage of generated queries that are syntactically identical to the ground truth.
    * **Logical Form Accuracy:** (More complex to implement) Evaluates if the generated query captures the correct logical intent, even if the syntax differs.
    * **LLM as a Judge (G-Eval):**
        * **Methodology:** Design prompts for a capable LLM (e.g., GPT-4 if allowed for evaluation, or a strong 7B reasoning model) to act as a judge.
        * **Rubric:** Define a clear scoring rubric (e.g., 1-5 scale for correctness, faithfulness to NL, schema adherence, executability).
        * **Pairwise Comparison:** Evaluate candidate queries against ground truth or other candidates.
        * **Bias Mitigation:** Be aware of potential biases in LLM judgments and design prompts to minimize them.
3.  **Experimentation & A/B Testing:**
    * For each component, systematically test different techniques and parameters.
    * Track performance (accuracy, latency, token usage) for each configuration.
    * Prioritize exploration over immediate state-of-the-art results, focusing on what works best for your 7B models and use case.
4.  **Error Analysis (SQL-CRAFT inspired):**
    * Categorize common failure modes (e.g., schema linking errors, incorrect joins, wrong aggregations, syntax errors).
    * Use insights from error analysis to refine components and prompting strategies.

---

## Phase 4: Integration with Chat LLM

1.  **Tool Definition:** Define your Text-to-SQL framework as a "tool" for a chat LLM, specifying its input (natural language question, schema context) and output (SQL query, execution result, error message).
2.  **Agent Orchestration:**
    * **Tool Calling:** Implement the logic for the chat LLM to decide *when* to invoke the Text-to-SQL tool based on user intent.
    * **Multi-turn Conversation Management:** Handle context, previous turns, and schema information across multiple user queries.
    * **Error Handling:** Present validation or execution errors gracefully to the user, potentially allowing for disambiguation or re-prompting.
    * **Security & Safety:** Implement guardrails to prevent malicious SQL injections or access to sensitive data (e.g., via schema redaction, query sanitization, or restricted database user).
3.  **User Experience:**
    * Provide clear responses to the user, including the generated SQL and its execution results.
    * Allow for follow-up questions or refinements.