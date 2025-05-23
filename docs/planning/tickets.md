# Project Tickets: Small Model Text-to-SQL Framework

---

## Phase 1: Project Setup & Foundational Research

### 1.1 Environment Setup
* **Ticket P1.1.1: Initialize Python Project & Virtual Environment**
    * **Description:** Create the project directory, initialize a Git repository, and set up a Python virtual environment (e.g., `venv` or `conda`).
    * **Deliverable:** Project structure with an active virtual environment and a `requirements.txt` file.
* **Ticket P1.1.2: Install Core Libraries**
    * **Description:** Install `transformers`, `torch` (or `tensorflow`), `langchain`, `sqlparse`, `pandas`, `numpy`, `scikit-learn`.
    * **Deliverable:** Updated `requirements.txt` and verified installations.
* **Ticket P1.1.3: Install Database Connector Libraries**
    * **Description:** Install database connectors like `psycopg2` (for PostgreSQL) and `sqlite3` (usually built-in, but confirm).
    * **Deliverable:** Updated `requirements.txt` and verified installations.
* **Ticket P1.1.4: Setup Local Test Database (SQLite)**
    * **Description:** Create an SQLite database. Ingest a small, representative subset of data and schema from BIRD/Spider datasets (e.g., 2-3 databases).
    * **Deliverable:** SQLite database file with sample data and schema; script to initialize the database.
* **Ticket P1.1.5: Implement Basic Logging Configuration**
    * **Description:** Set up a basic logging mechanism (e.g., using Python's `logging` module) to output informative messages with timestamps and levels.
    * **Deliverable:** A `logger.py` utility or configuration in the main script.
* **Ticket P1.1.6: Implement Basic Configuration Management**
    * **Description:** Create a system for managing configurations (e.g., model names, paths, database credentials (if any), API keys) using a config file (e.g., YAML, JSON, or `.env`).
    * **Deliverable:** A configuration loading utility and a sample config file.

---

### 1.2 Model Selection & Preparation
* **Ticket P1.2.1: Research & Shortlist 7B Text-to-SQL Models**
    * **Description:** Investigate pre-trained/fine-tuned 7B models (Mistral 7B, Llama2 7B, Gemma 7B, DeciLM 7B) focusing on those fine-tuned for SQL generation. Document Hugging Face paths, paper links, and reported performance on Spider/BIRD if available.
    * **Deliverable:** A summary document/notes with at least 3-4 candidate models, their pros, cons, and SQL-specific fine-tuning details.
* **Ticket P1.2.2: Document Licensing & Deployment for Text-to-SQL Models**
    * **Description:** For the shortlisted Text-to-SQL models, research and document their specific licensing terms and any particular deployment requirements or limitations.
    * **Deliverable:** Updated summary document with licensing and deployment information for each shortlisted model.
* **Ticket P1.2.3: Select Initial 1-2 Text-to-SQL Models**
    * **Description:** Based on research (P1.2.1, P1.2.2), select 1-2 Text-to-SQL models for initial experimentation.
    * **Deliverable:** Documented decision and rationale.
* **Ticket P1.2.4: Research & Shortlist 7B Reasoning Models**
    * **Description:** Investigate 7B models known for strong mathematical or code reasoning (e.g., MiMo-7B, Phi-3 models with reasoning capabilities). Document Hugging Face paths and relevant capabilities.
    * **Deliverable:** A summary document/notes with at least 2-3 candidate reasoning models.
* **Ticket P1.2.5: Document Licensing & Deployment for Reasoning Models**
    * **Description:** For the shortlisted reasoning models, research and document their specific licensing terms and deployment requirements.
    * **Deliverable:** Updated summary document with licensing and deployment information.
* **Ticket P1.2.6: Select Initial 1-2 Reasoning Models**
    * **Description:** Based on research (P1.2.4, P1.2.5), select 1-2 reasoning models.
    * **Deliverable:** Documented decision and rationale.
* **Ticket P1.2.7: Develop Script for Loading Selected Text-to-SQL Model(s)**
    * **Description:** Create a Python script/module to load the selected Text-to-SQL model(s) into memory or set up an inference pipeline using HuggingFace `transformers`.
    * **Deliverable:** Modular Python code for model loading and a simple test inference.
* **Ticket P1.2.8: Develop Script for Loading Selected Reasoning Model(s)**
    * **Description:** Create a Python script/module to load the selected reasoning model(s).
    * **Deliverable:** Modular Python code for model loading and a simple test inference.

---

### 1.3 Core Utilities
* **Ticket P1.3.1: Develop Database Connector Abstraction**
    * **Description:** Create a Python class/module that abstracts database connections (connect, disconnect) and query execution (fetch results, handle basic errors). Initially target SQLite.
    * **Deliverable:** `DatabaseConnector` class/module with methods for `connect`, `disconnect`, `execute_query`.
* **Ticket P1.3.2: Implement Schema Introspection Function**
    * **Description:** Using the `DatabaseConnector`, implement a function to retrieve schema information from the connected database (table names, column names, data types, PKs, FKs).
    * **Deliverable:** `get_schema_details(db_connector)` function returning structured schema info.
* **Ticket P1.3.3: Develop Schema Loader Utility (from DDL)**
    * **Description:** Create a utility to parse `CREATE TABLE` statements from a file or string and extract schema information.
    * **Deliverable:** `load_schema_from_ddl(ddl_string_or_path)` function.
* **Ticket P1.3.4: Develop Schema-to-Plain-Text Utility**
    * **Description:** Create a utility to convert the structured schema (from P1.3.2 or P1.3.3) into a plain text representation suitable for LLM prompts.
    * **Deliverable:** `format_schema_plain_text(schema_info)` function.
* **Ticket P1.3.5: Develop Schema-to-JSON Utility**
    * **Description:** Create a utility to convert the structured schema into a JSON representation suitable for LLM prompts or structured processing.
    * **Deliverable:** `format_schema_json(schema_info)` function.
* **Ticket P1.3.6: Develop BIRD/Spider Dataset Loader**
    * **Description:** Create utilities to load samples (NL question, gold SQL query, database ID) from BIRD and Spider datasets (JSON files).
    * **Deliverable:** Functions to load and iterate through dataset samples.
* **Ticket P1.3.7: Implement Parser for BIRD/Spider Schema Files**
    * **Description:** Develop a parser for the `tables.json` (Spider) or equivalent schema files in BIRD that accompany the datasets, to be used if direct DB introspection isn't preferred for dataset schema.
    * **Deliverable:** Function to parse schema files from these datasets.

---

## Phase 2: Modular Component Development & Exploration

### 2.1 Component 1: Database Tables Pruning & Schema Presentation
* **Ticket P2.1.1: Implement Schema Presentation: Plain Text/Concatenated DDL**
    * **Description:** Implement the generation of schema context using full `CREATE TABLE` statements.
    * **Deliverable:** Function `present_schema_ddl(db_id, tables_list)`.
* **Ticket P2.1.2: Implement Schema Presentation: JSON Format**
    * **Description:** Implement schema presentation in a structured JSON format, including table names, column names, data types, PKs, FKs (with explicit linking details), and placeholders for natural language descriptions.
    * **Deliverable:** Function `present_schema_json(db_id, tables_list)`.
* **Ticket P2.1.3: Research M-Schema Feasibility**
    * **Description:** Review the M-Schema format (XiYan-SQL) and assess its feasibility for 7B models, considering token limits and complexity.
    * **Deliverable:** Short research note on M-Schema applicability.
* **Ticket P2.1.4: Implement Explicit FK Encoding in Schema Formats**
    * **Description:** Ensure both plain text and JSON schema presentation formats explicitly denote foreign key relationships (e.g., `FOREIGN KEY (col) REFERENCES other_table(other_col)` or a dedicated FK list per table).
    * **Deliverable:** Updated schema presentation functions from P2.1.1 and P2.1.2.
* **Ticket P2.1.5: Implement Sample Data Inclusion in Schema Presentation**
    * **Description:** Add functionality to optionally include a few sample data rows (e.g., 3 rows) per table in the schema presentation.
    * **Deliverable:** Modification to schema presentation functions to include sample data.
* **Ticket P2.1.6: Implement Table Pruning: Semantic Similarity (Embeddings)**
    * **Description:** Use sentence transformers to generate embeddings for the input question and table/column names/descriptions. Implement a function to select top-k relevant tables based on cosine similarity.
    * **Deliverable:** `prune_tables_semantic(question, schema_info, top_k)` function.
* **Ticket P2.1.7: Implement Table Pruning: DFIN-SQL "Focused Schema" (RAG-like)**
    * **Description:** Implement a RAG-like retrieval of relevant schema subsets. This will involve prompting a reasoning LLM with the question and full schema (or chunks) to identify relevant tables.
    * **Deliverable:** `prune_tables_llm_rag(question, full_schema_str, reasoning_llm)` function.
* **Ticket P2.1.8: Research Graph-based Table Pruning**
    * **Description:** Briefly research graph-based schema representations and algorithms (e.g., shortest path between entities mentioned in the question) for table pruning. Outline a potential implementation.
    * **Deliverable:** Research note with an outlined approach.
* **Ticket P2.1.9: Implement Table Pruning: LLM-based Selector Agent**
    * **Description:** Use a reasoning LLM (or a fine-tuned 7B model) with a specific prompt to act as a "selector agent," taking the question and full schema to output a list of relevant table names.
    * **Deliverable:** `prune_tables_selector_agent(question, full_schema_str, reasoning_llm)` function.
* **Ticket P2.1.10: Develop Evaluation for Schema Presentation & Pruning**
    * **Description:** Create a script/notebook to evaluate different combinations of schema presentation and pruning. Metrics: table recall (requires gold relevant tables), schema token count.
    * **Deliverable:** Evaluation script and a results summary template.
* **Ticket P2.1.11: Test & Evaluate Schema/Pruning Combination 1**
    * **Description:** Test [Plain Text DDL + Semantic Pruning]. Evaluate using the framework from P2.1.10 on a subset of the custom/Spider dataset.
    * **Deliverable:** Results for Combination 1.
* **Ticket P2.1.12: Test & Evaluate Schema/Pruning Combination 2**
    * **Description:** Test [JSON Format + LLM Selector Agent Pruning]. Evaluate.
    * **Deliverable:** Results for Combination 2.
* **Ticket P2.1.13: Document Findings: Schema Presentation & Pruning**
    * **Description:** Consolidate results from P2.1.11, P2.1.12 (and any other combinations tested) and document pros/cons of each approach.
    * **Deliverable:** Summary document.

---

### 2.2 Component 2: Relevant Columns Linking
* **Ticket P2.2.1: Implement Column Linking: Semantic Similarity**
    * **Description:** After tables are pruned, apply embedding-based matching between question terms and column names/descriptions within those tables.
    * **Deliverable:** `link_columns_semantic(question, pruned_tables_schema_info, top_k_cols_per_table)` function.
* **Ticket P2.2.2: Implement Column Linking: LLM-based Filtering**
    * **Description:** Provide the LLM with the selected tables (and their full column info) and the question, prompting it to list the most relevant columns.
    * **Deliverable:** `link_columns_llm(question, pruned_tables_schema_info, text_to_sql_llm)` function.
* **Ticket P2.2.3: Research DFIN-SQL & MAC-SQL Column Selection**
    * **Description:** Adapt strategies from DFIN-SQL/MAC-SQL for prompt-based column selection, focusing on how to guide the LLM.
    * **Deliverable:** Research note with prompting strategies.
* **Ticket P2.2.4: Implement Column Linking: Heuristic-based**
    * **Description:** Implement simple heuristics, e.g., always include primary keys of selected tables, or columns explicitly mentioned or strongly implied by question keywords.
    * **Deliverable:** `link_columns_heuristic(question, pruned_tables_schema_info)` function.
* **Ticket P2.2.5: Integrate Column Linking with Table Pruning Output**
    * **Description:** Ensure the column linking component can take the output of any table pruning method and further refine the schema string.
    * **Deliverable:** A wrapper function or clear workflow integrating table pruning and column linking.
* **Ticket P2.2.6: Develop Evaluation for Column Linking**
    * **Description:** Create a script/notebook to evaluate column linking strategies. Metrics: column recall/precision (requires gold relevant columns), final schema token count.
    * **Deliverable:** Evaluation script and results summary template.
* **Ticket P2.2.7: Test & Evaluate Column Linking Strategies**
    * **Description:** Test at least two column linking strategies (e.g., Semantic Similarity vs. LLM-based) and document results.
    * **Deliverable:** Evaluation results.
* **Ticket P2.2.8: Document Findings: Column Linking**
    * **Description:** Summarize the effectiveness of different column linking techniques.
    * **Deliverable:** Summary document.

---

### 2.3 Component 3: Multi-Path Generation
* **Ticket P2.3.1: Implement SQL Generation: Direct Prompting**
    * **Description:** Implement standard zero-shot or few-shot prompting with a selected Text-to-SQL 7B model. Include beam search to get multiple candidates.
    * **Deliverable:** `generate_sql_direct(question, schema_context, llm, num_candidates)` function.
* **Ticket P2.3.2: Implement SQL Generation: Chain-of-Thought (CoT)**
    * **Description:** Implement CoT prompting, instructing the LLM to generate intermediate reasoning steps before the SQL. Include beam search.
    * **Deliverable:** `generate_sql_cot(question, schema_context, llm, num_candidates)` function.
* **Ticket P2.3.3: Implement Question Decomposition (LLM-based)**
    * **Description:** Use a reasoning LLM to decompose complex NL questions into simpler sub-questions.
    * **Deliverable:** `decompose_question_llm(question, reasoning_llm)` function.
* **Ticket P2.3.4: Implement Sub-Question SQL Generation & Combination**
    * **Description:** Generate SQL for each sub-question (using direct or CoT). Implement logic to combine sub-queries (e.g., LLM-based merging or rule-based for JOIN/UNION).
    * **Deliverable:** `generate_sql_decomposed(decomposed_questions, schema_context, llm, reasoning_llm_for_merge)` function.
* **Ticket P2.3.5: Research Constraint-based Generation (LogicalBeam)**
    * **Description:** Briefly research the feasibility of integrating CFGs or other constraint mechanisms with 7B models in Python (e.g., libraries like `guidance` or `outlines` for HuggingFace models).
    * **Deliverable:** Research note on feasibility and potential tools.
* **Ticket P2.3.6: Implement Ensemble Generation: Varied Prompts & Parameters**
    * **Description:** Set up a framework to run multiple generation strategies (e.g., Direct + CoT) and vary beam search parameters (temperature, top-k/p) to generate a diverse set of candidates.
    * **Deliverable:** `generate_sql_ensemble(question, schema_context, llm_configs_list)` function.
* **Ticket P2.3.7: Implement Generation Path: No Pruning/Linking Control**
    * **Description:** Create a generation path that uses the full schema (or minimal pruning) to act as a control and test the impact of aggressive pruning/linking.
    * **Deliverable:** Configuration option in the generation framework.
* **Ticket P2.3.8: Develop Evaluation for Generation Strategies**
    * **Description:** Set up an initial evaluation for generated SQL. Metrics: % syntactically valid, % executable (even if not correct yet), diversity of candidates (e.g., BLEU score against each other if meaningful, or manual inspection).
    * **Deliverable:** Evaluation script.
* **Ticket P2.3.9: Test & Document Individual Generation Strategies**
    * **Description:** Run each implemented generation strategy (Direct, CoT, Decomposition) on a small set of diverse questions. Document qualitative observations and initial metrics.
    * **Deliverable:** Notes and preliminary results for each strategy.

---

### 2.4 Component 4: Validator
* **Ticket P2.4.1: Implement Syntactic Validation (`sqlparse`)**
    * **Description:** Use `sqlparse` to check generated SQL queries for basic syntax errors.
    * **Deliverable:** `validate_syntax_sqlparse(sql_query)` function.
* **Ticket P2.4.2: Implement Database Execution Validation**
    * **Description:** Attempt to execute the SQL query against the target database. Catch and categorize exceptions (syntax, invalid objects, etc.).
    * **Deliverable:** `validate_execution(sql_query, db_connector)` function returning success/failure and error message.
* **Ticket P2.4.3: Research Python DCG/CFG Libraries for SQL**
    * **Description:** Investigate Python libraries for definite clause grammars or context-free grammars that could be adapted for SQL schema-aware validation *before* execution. Assess feasibility.
    * **Deliverable:** Research note on DCG/CFG library options and integration complexity.
* **Ticket P2.4.4: Implement LLM Self-Correction (ReFoRCE/DART-SQL inspired)**
    * **Description:** If a query fails execution, provide the LLM with the failed query and the error message, prompting it to correct and regenerate the query.
    * **Deliverable:** `self_correct_sql_llm(original_sql, error_message, question, schema_context, llm)` function.
* **Ticket P2.4.5: Implement Error Categorization & Targeted Retries**
    * **Description:** Categorize SQL errors. Implement a retry mechanism (e.g., 1-3 retries) that uses self-correction or simple regeneration based on the error type.
    * **Deliverable:** Logic within the validator to manage retries and call self-correction.
* **Ticket P2.4.6: Develop Multi-Stage Validator Pipeline**
    * **Description:** Integrate validation steps: syntactic check -> (DCG if feasible) -> execution -> self-correction/retries.
    * **Deliverable:** `validate_pipeline(sql_query, db_connector, question, schema_context, llm)` function.
* **Ticket P2.4.7: Test & Evaluate Validator Component**
    * **Description:** Evaluate the validator on a set of generated queries (including intentionally flawed ones). Metrics: % of errors caught by each stage, success rate of self-correction.
    * **Deliverable:** Evaluation results for the validator.
* **Ticket P2.4.8: Document Findings: Validation Techniques**
    * **Description:** Summarize the effectiveness of different validation and correction strategies.
    * **Deliverable:** Summary document.

---

### 2.5 Component 5: Reranker
* **Ticket P2.5.1: Implement Reranking Criterion: Execution Success**
    * **Description:** Use the boolean flag from the Validator indicating successful execution as a primary reranking criterion.
    * **Deliverable:** Function to extract execution status for each candidate.
* **Ticket P2.5.2: Implement Reranking Criterion: LLM Confidence Score**
    * **Description:** Use a reasoning LLM to assess the semantic correctness/relevance of (executable) SQL relative to the NL question. Prompt it to output a confidence score (e.g., 1-5).
    * **Deliverable:** `get_llm_confidence(nl_question, sql_query, reasoning_llm)` function.
* **Ticket P2.5.3: Implement Reranking Criterion: Semantic Similarity (NL-SQL)**
    * **Description:** Research and implement using a cross-encoder or bi-encoder to score semantic similarity between the NL question and the generated SQL (or a natural language explanation of the SQL if generated).
    * **Deliverable:** `get_nl_sql_similarity(nl_question, sql_query, similarity_model)` function and model selection notes.
* **Ticket P2.5.4: Implement Reranking Criterion: Query Complexity**
    * **Description:** Implement a simple metric for query complexity (e.g., length, number of keywords, AST node count from `sqlparse`).
    * **Deliverable:** `get_query_complexity(sql_query)` function.
* **Ticket P2.5.5: Implement Reranking Method: Rule-based Hierarchy**
    * **Description:** Develop a rule-based reranker that prioritizes candidates based on a hierarchy (e.g., 1. Executable, 2. Highest LLM Confidence, 3. Lowest Complexity).
    * **Deliverable:** `rerank_rule_based(candidates_with_features)` function.
* **Ticket P2.5.6: Implement Reranking Method: Reciprocal Rank Fusion (RRF)**
    * **Description:** Implement RRF to combine scores from multiple criteria (execution, LLM confidence, similarity) if normalized appropriately.
    * **Deliverable:** `rerank_rrf(candidates_with_scores)` function.
* **Ticket P2.5.7: Develop Reranker Evaluation Framework**
    * **Description:** Design an evaluation for the reranker. Metrics: accuracy of the top-1 selected query against ground truth (using execution accuracy from Phase 3).
    * **Deliverable:** Evaluation script.
* **Ticket P2.5.8: Test & Evaluate Reranker Combinations**
    * **Description:** Test at least 2-3 different combinations of criteria and weighting/fusion methods.
    * **Deliverable:** Reranker evaluation results.
* **Ticket P2.5.9: Document Findings: Reranking Strategies**
    * **Description:** Summarize which reranking criteria and methods perform best.
    * **Deliverable:** Summary document.

---

### 2.6 Component 6 (Optional): Refiner
* **Ticket P2.6.1: Implement Basic LLM-based Refinement**
    * **Description:** Take the top-1 or top-2 queries from the reranker. If there's a known (simple) issue or if execution results are available and differ from expectation (on dev set), prompt an LLM with the query, the issue/context, and ask for a refined version.
    * **Deliverable:** `refine_query_llm(sql_query, issue_context, question, schema_context, llm)` function.
* **Ticket P2.6.2: Implement LLM-based Query Optimization Prompt**
    * **Description:** Prompt the LLM to optimize a given SQL query for performance or readability (e.g., convert subqueries to joins, simplify clauses) without changing its semantics.
    * **Deliverable:** `optimize_query_llm(sql_query, schema_context, llm)` function.
* **Ticket P2.6.3: Test & Evaluate Refiner Component**
    * **Description:** Evaluate the refiner on a small set of queries where initial versions have known flaws or suboptimal structure. Metrics: % improvement in execution accuracy or successful optimization.
    * **Deliverable:** Refiner evaluation results.
* **Ticket P2.6.4: Document Findings: Refinement Strategies**
    * **Description:** Summarize the effectiveness of the implemented refinement approaches.
    * **Deliverable:** Summary document.

---

## Phase 3: Evaluation & Iteration

### 3.1 Dataset Preparation
* **Ticket P3.1.1: Create Custom Dataset (Small, Representative)**
    * **Description:** Create a small dataset (15-25 samples) of NL questions, corresponding ground truth SQL queries, and expected execution results, reflecting your specific target use case or challenging scenarios.
    * **Deliverable:** Custom dataset in a structured format (e.g., JSON).
* **Ticket P3.1.2: Setup Evaluation on BIRD Subset**
    * **Description:** Prepare scripts to run the full Text-to-SQL pipeline and evaluate on a defined subset of the BIRD development set.
    * **Deliverable:** Evaluation script for BIRD.
* **Ticket P3.1.3: Setup Evaluation on Spider Subset**
    * **Description:** Prepare scripts to run the full Text-to-SQL pipeline and evaluate on a defined subset of the Spider development set.
    * **Deliverable:** Evaluation script for Spider.

---

### 3.2 Evaluation Metrics
* **Ticket P3.2.1: Implement Execution Accuracy Metric**
    * **Description:** Implement a function to execute a generated SQL query and compare its results against the ground truth query's results (requires careful handling of order, value types). Use BIRD's official `evaluator.py` as a reference for execution and value comparison.
    * **Deliverable:** `calculate_execution_accuracy(generated_sql, ground_truth_sql, db_id, db_connector)` function.
* **Ticket P3.2.2: Implement Exact Match Accuracy Metric**
    * **Description:** Implement a function for Spider-style exact match accuracy (string comparison after some normalization). Use Spider's official `evaluation.py` for guidance.
    * **Deliverable:** `calculate_exact_match_accuracy(generated_sql, ground_truth_sql)` function.
* **Ticket P3.2.3: Design Prompts & Rubric for LLM-as-a-Judge (G-Eval)**
    * **Description:** Design prompts for a capable LLM (e.g., GPT-4 or a strong 7B reasoning model) to evaluate generated SQL. Define a clear scoring rubric (1-5 scale for correctness, faithfulness, schema adherence, executability).
    * **Deliverable:** Prompt templates and rubric document.
* **Ticket P3.2.4: Implement G-Eval Script**
    * **Description:** Create a script to automate LLM-based evaluation using the designed prompts and rubric. Consider pairwise comparison or direct scoring.
    * **Deliverable:** G-Eval script.
* **Ticket P3.2.5: Document G-Eval Bias Mitigation Strategies**
    * **Description:** Research and document potential biases in LLM judgments and outline strategies to minimize them in prompt design and interpretation of results.
    * **Deliverable:** Short document on bias mitigation.

---

### 3.3 Experimentation & A/B Testing
* **Ticket P3.3.1: Design Initial End-to-End Experiment Plan**
    * **Description:** Outline an initial experiment comparing at least two distinct end-to-end configurations of the framework (e.g., different pruning + generation + reranking choices). Specify metrics to track (ExecAcc, EM, Latency, Token Usage).
    * **Deliverable:** Experiment plan document.
* **Ticket P3.3.2: Implement Centralized Metrics Tracking**
    * **Description:** Implement a system (e.g., CSV logging, simple database, or MLflow if overkill isn't an issue) to track performance metrics for each experimental run.
    * **Deliverable:** Metrics logging utility.
* **Ticket P3.3.3: Conduct and Analyze First End-to-End Experiment**
    * **Description:** Run the experiment outlined in P3.3.1 on the custom dataset and a Spider/BIRD subset. Analyze and document the results.
    * **Deliverable:** Results and analysis report for the first experiment.

---

### 3.4 Error Analysis
* **Ticket P3.4.1: Develop Error Categorization Framework (SQL-CRAFT inspired)**
    * **Description:** Based on initial experiments, develop a framework for categorizing common failure modes (e.g., schema linking errors, incorrect joins, wrong aggregations, syntax errors not caught, hallucinated columns/tables).
    * **Deliverable:** Error categorization guide/document.
* **Ticket P3.4.2: Perform Systematic Error Analysis**
    * **Description:** On a batch of ~50-100 failed queries from experiments, manually categorize errors according to the framework.
    * **Deliverable:** Spreadsheet or document with categorized errors.
* **Ticket P3.4.3: Document Insights from Error Analysis**
    * **Description:** Summarize key findings from the error analysis. Identify the most common error types and link them to specific components or prompting strategies that need refinement.
    * **Deliverable:** Error analysis insights report.

---

## Phase 4: Integration with Chat LLM (Simplified for Research Focus)

### 4.1 Tool Definition
* **Ticket P4.1.1: Define Text-to-SQL Framework as a Langchain Tool**
    * **Description:** Wrap the core Text-to-SQL generation pipeline (from question + schema to SQL + result/error) as a Langchain `Tool`.
    * **Input:** Natural language question, schema context (string or structured).
    * **Output:** SQL query (string), execution result (string/object), or error message (string).
    * **Deliverable:** Python class inheriting from `langchain.tools.BaseTool`.

---

### 4.2 Agent Orchestration (Simplified)
* **Ticket P4.2.1: Implement Basic Agent with Tool Calling**
    * **Description:** Create a simple Langchain agent (e.g., using a function-calling enabled LLM or a ReAct agent) that can decide to use the Text-to-SQL tool.
    * **Deliverable:** Python script demonstrating the agent invoking the tool for a relevant query.
* **Ticket P4.2.2: Implement Basic Security Guardrail: Query Sanitization Research**
    * **Description:** Research basic SQL query sanitization techniques or libraries in Python to prevent obvious SQL injection patterns (as a conceptual safety layer, full security is complex).
    * **Deliverable:** Research note on simple sanitization approaches.

---

### 4.3 User Experience (Simplified for CLI/Testing)
* **Ticket P4.3.1: Develop CLI for Chat LLM Interaction**
    * **Description:** Create a command-line interface where a user can type a question. The agent (P4.2.1) processes it, potentially calls the Text-to-SQL tool, and prints the SQL and its execution result or error.
    * **Deliverable:** Python script for CLI interaction.

---