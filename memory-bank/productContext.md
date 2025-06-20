# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-06-19 23:04:00 - Log of updates made will be appended as footnotes to the end of this file.

*
2025-05-31 01:36:13 - Initial population from docs/planning/project_desc.md

## Project Goal

* Develop a Python-based Text-to-SQL framework using 7B parameter models. The framework will focus on modularity, diverse candidate generation, and iterative refinement, with an emphasis on research and testing various approaches to achieve robust and accurate SQL generation from natural language queries.

## Key Features

*   **Modular Design:** Components for schema pruning, column linking, multi-path SQL generation, validation, reranking, and optional refinement.
*   **Small Model Focus:** Utilizes 7B parameter models for both Text-to-SQL and reasoning tasks.
*   **Flexible Schema Handling:** Supports various schema presentation formats (Plain Text DDL, JSON, M-Schema) and table/column pruning techniques.
*   **Agent-based Context Retrieval:** Utilizes an agent (`InformationRetriever`) to intelligently extract keywords from natural language and retrieve the most relevant table/column context using semantic search.
*   **Diverse Generation Strategies:** Implements multiple SQL generation paths including direct prompting, Chain-of-Thought, query decomposition, and ensemble methods.
*   **Robust Validation & Correction:** Multi-stage validation including syntactic checks, database execution, and LLM-based self-correction.
*   **Advanced Reranking:** Employs multi-criteria reranking to select the best SQL candidate.
*   **Comprehensive Evaluation:** Evaluation framework using custom datasets and public benchmarks like BIRD/Spider, with metrics such as execution accuracy and LLM-as-a-judge.
*   **Chat LLM Integration:** Designed to be integrated as a tool within a larger chat LLM system.

## Overall Architecture

*   The framework is designed with a phased development approach:
    *   **Phase 1: Project Setup & Foundational Research:** Establishes the environment, selects models (7B Text-to-SQL and reasoning models), and develops core utilities for database interaction and dataset handling.
    *   **Phase 2: Modular Component Development:** Focuses on building and exploring techniques for key pipeline stages:
        *   Database Tables Pruning & Schema Presentation
        *   Relevant Columns Linking (Enhanced by Semantic Search)
        *   Multi-Path SQL Generation
        *   SQL Validator (including self-correction)
        *   SQL Reranker
        *   Optional SQL Refiner
    *   **Phase 3: Evaluation & Iteration:** Involves preparing datasets, defining evaluation metrics (execution accuracy, exact match, LLM-as-a-judge), conducting experiments, and performing error analysis.
    *   **Phase 4: Integration with Chat LLM:** Defines the framework as a tool for a chat LLM, manages agent orchestration, handles multi-turn conversations, and ensures security.
*   The core architecture is a pipeline of these modular components, transforming a natural language question and database schema into an executable SQL query. An `InformationRetriever` agent acts as a preliminary step, using a vector database (ChromaDB) to perform semantic search on schema information, providing highly relevant context to the main pipeline.