# src/prompts/keyword_phrases_extraction.py
"""
Prompt and few-shot examples for extracting keywords and phrases from a user query.
"""

# Few-shot examples demonstrating the desired DICTIONARY output format.
# This is intended to be injected into the PROMPT's {FEWSHOT EXAMPLES} placeholder.
# The goal is for these examples to guide the LLM to output a dictionary,
# even if the main PROMPT text asks for a list.
FEW_SHOT_EXAMPLES_FOR_DICT_OUTPUT_STR = """
Question: "Show me all customers from Germany who ordered product X"
Hint: "Focus on location, customer entity, and specific product mentions."
Output:
{"keywords": ["customers", "product"], "phrases": ["Germany", "product X"]}

Question: "List the top 5 employees by salary in the sales department"
Hint: "Consider job roles, compensation, and organizational units."
Output:
{"keywords": ["employees", "salary", "department"], "phrases": ["sales"]}

Question: "Find orders placed after January 1st, 2023 for user_id 123"
Hint: "Look for date constraints and user identifiers."
Output:
{"keywords": ["orders", "user_id"], "phrases": ["January 1st, 2023", "123"]}

Question: "What are the most common issues reported for the 'Alpha' project last quarter?"
Hint: "Identify the project name, timeframe, and the type of information requested (issues)."
Output:
{"keywords": ["issues", "project"], "phrases": ["Alpha", "last quarter"]}
"""

PROMPT = """Objective: Analyze the given question and hint to identify and extract
keywords, keyphrases, and named entities. These elements are crucial for
understanding the core components of the inquiry and the guidance provided.
This process involves recognizing and isolating significant terms and phrases
that could be instrumental in formulating searches or queries related to the
posed question.
Instructions:
1. Read the Question Carefully: Understand the primary focus and specific
details of the question. Look for any named entities (such as organizations,
locations, etc.), technical terms, and other phrases that encapsulate important
aspects of the inquiry.
2. Analyze the Hint: The hint is designed to direct attention toward certain
elements relevant to answering the question. Extract any keywords, phrases, or
named entities that could provide further clarity or direction in formulating
an answer.
3. Extract Keyphrases and Entities: Combine your findings from both the question
and the hint into a single JSON map. This dictionary should contain:
- Keywords: Single words that capture essential aspects of the question or
hint.
- Phrases: Short phrases or named entities that represent specific concepts,
locations, organizations, or other significant details.
Ensure to maintain the original phrasing or terminology used in the question
and hint. 
{FEWSHOT_EXAMPLES}
Task:
Given the following question and hint, identify and exract all relevant keywords,
phrases, and named entities.
Question: {QUESTION}
Hint: {HINT}
Please provide your findings as a JSON map similar to the examples, capturing the essence of both
the question and hint through the identified terms and phrases.
Only output the JSON, no explanations needed."""