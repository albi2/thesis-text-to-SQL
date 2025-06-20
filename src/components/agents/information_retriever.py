# src/components/agents/information_retriever.py
"""
InformationRetriever agent for extracting keywords, phrases, and relevant context.
"""
import json # Changed from ast to json
from typing import Dict, List, Any

from common.config.config_helper import ConfigurationHelper
from components.models.embedding_model_facade import SentenceTransformerEmbeddingFacade
from components.models.reasoning_model_facade import ReasoningModelFacade
from infrastructure.vector_db.chroma_client import ChromaClient
from prompts.keyword_phrases_extraction import PROMPT, FEW_SHOT_EXAMPLES_FOR_DICT_OUTPUT_STR
from util.constants import HuggingFaceModelConstants, PreprocessingConstants


class InformationRetriever:
    """
    Agent responsible for extracting keywords and phrases from user queries
    and retrieving relevant contextual information from a knowledge base.
    """

    def __init__(self, reasoning_model_name: str = None):
        """
        Initializes the InformationRetriever.

        Args:
            reasoning_model_name (str, optional): The name or path of the reasoning model to use.
                If None, the default reasoning model will be used.
        """
        self.reasoning_model = ReasoningModelFacade(model_name=reasoning_model_name)

        # Initialize ConfigurationHelper to load ChromaDB settings
        self.config_helper = ConfigurationHelper()
        chroma_config = self.config_helper.get_config('chroma_db.yaml', 'chroma_db')

        chroma_host = chroma_config.get('host', PreprocessingConstants.DEFAULT_CHROMA_HOST)
        chroma_port = chroma_config.get('port', PreprocessingConstants.DEFAULT_CHROMA_PORT)

        # Initialize Embedding Facade
        self.embedding_facade = SentenceTransformerEmbeddingFacade(
            model_name_or_path=HuggingFaceModelConstants.DEFAULT_EMBEDDING_MODEL,
        )

        # Initialize ChromaClient
        self.chroma_client = ChromaClient(
            host=chroma_host,
            port=chroma_port,
            embedding_facade=self.embedding_facade
        )

        # Store collection name
        self.column_collection_name = PreprocessingConstants.COLUMN_COLLECTION_NAME


    def extract_keywords(self, user_query: str, hint: str = "") -> Dict[str, List[str]]:
        """
        Extracts main entities (keywords) and main phrases (values) from a user query.

        This method uses the original PROMPT from keyword_phrases_extraction.py,
        injecting FEW_SHOT_EXAMPLES_FOR_DICT_OUTPUT_STR into its
        {FEWSHOT EXAMPLES} placeholder. The injected examples are designed to
        guide the LLM to return a Python dictionary string with "keywords" and
        "phrases" keys, despite the original prompt's text asking for a list.

        Args:
            user_query: The natural language query from the user (maps to QUESTION).
            hint: An optional hint to guide extraction (maps to HINT).

        Returns:
            A dictionary with "keywords" and "phrases" as keys,
            e.g., {"keywords": ["kw1"], "phrases": ["phrase1", "phrase two"]}.
            Returns an empty dict with empty lists if extraction or parsing fails.
        """
        # Inject the dictionary-output examples into the original prompt
        formatted_prompt = PROMPT.format(FEWSHOT_EXAMPLES = FEW_SHOT_EXAMPLES_FOR_DICT_OUTPUT_STR, QUESTION=user_query, HINT=hint if hint else "No hint provided.")

        keywords_list: List[str] = []
        phrases_list: List[str] = []

        try:
            # Use the 'query' method from ReasoningModelFacade
            response_text = self.reasoning_model.query(formatted_prompt)
            
            # Expecting the LLM to output a JSON string representing a dictionary.
            parsed_response = json.loads(response_text.strip())
            print(f"LLM Response for keyword extraction: {parsed_response}")

            if isinstance(parsed_response, dict):
                keywords = parsed_response.get("keywords", [])
                phrases = parsed_response.get("phrases", [])

                if isinstance(keywords, list) and all(isinstance(kw, str) for kw in keywords):
                    keywords_list = [kw.strip() for kw in keywords if kw.strip()]
                else:
                    # TODO: Log warning - "keywords" in response is not a list of strings or malformed.
                    pass
                
                if isinstance(phrases, list) and all(isinstance(ph, str) for ph in phrases):
                    phrases_list = [ph.strip() for ph in phrases if ph.strip()]
                else:
                    # TODO: Log warning - "phrases" in response is not a list of strings or malformed.
                    pass
            else:
                # LLM did not return a dictionary as expected after parsing
                # TODO: Log this unexpected format after json.loads (not a dict)
                pass

        except json.JSONDecodeError as e:
            # Handle cases where the response is not a valid JSON string
            # TODO: Log parsing error: f"Error parsing LLM response as JSON for keyword extraction: {e}. Response: {response_text}"
            pass # Returns empty lists
        except Exception as e:
            # Catch any other unexpected errors during LLM call or parsing
            # TODO: Log generic error: f"Unexpected error in extract_keywords: {e}"
            pass # Returns empty lists
        return {"keywords": keywords_list, "phrases": phrases_list}

    def retrieve_entities(self, keywords: List[str], phrases: List[str]) -> List[str]:
        """
        Placeholder method to retrieve relevant entities (e.g., tables) based on
        keywords and phrases. The goal is to find tables whose columns might
        contain values similar to the provided phrases.

        Args:
            keywords: A list of keywords extracted from the user query.
            phrases: A list of phrases (potential data values) from the user query.

        Returns:
            A list of relevant entity names (e.g., table names).
            Currently returns an empty list.
        """
        # TODO: Implement logic to find relevant tables/entities.
        # This will likely involve checking column contents or metadata
        # against the provided phrases, possibly using the schema information
        # or a more direct database lookup if feasible.
        return []

    def retrieve_context(self, keywords: List[str], question: str, k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves the top-k most relevant column descriptions (or names)
        from the ChromaDB collection based on semantic similarity to the input keywords.

        Args:
            keywords: A list of keywords to search for.
            k: The number of top relevant columns to retrieve for each keyword.

        Returns:
            A dictionary where keys are input keywords and values are lists of
            dictionaries, each representing a relevant column:
            e.g., {"keyword1": [{"column_name": "col_a", "table_name": "table_x", "description": "desc_a"}, ...]}
            Returns an empty dictionary if no keywords are provided or an error occurs during retrieval.
        """
        if not keywords:
            return {}

        retrieved_contexts: Dict[str, List[Dict[str, Any]]] = {}

        for keyword in keywords:
            if not keyword.strip(): # Skip empty or whitespace-only keywords
                retrieved_contexts[keyword] = []
                continue
            try:
                question_and_keyword = question + " " + keyword 
                query_results = self.chroma_client.query_collection(
                    collection_name=self.column_collection_name,
                    query_texts=[question_and_keyword],
                    n_results=k,
                    # include=["metadatas", "documents"] # Ensure documents (descriptions) are included
                )

                keyword_contexts: List[Dict[str, Any]] = []
                if query_results and query_results.get("documents") and query_results.get("metadatas"):
                    docs_for_keyword = query_results["documents"][0] if query_results["documents"] else []
                    metadatas_for_keyword = query_results["metadatas"][0] if query_results["metadatas"] else []

                    for doc_text, metadata in zip(docs_for_keyword, metadatas_for_keyword):
                        if metadata and 'column_name' in metadata and 'table_name' in metadata:
                            keyword_contexts.append({
                                "column_name": metadata['column_name'],
                                "table_name": metadata['table_name'],
                                "description": doc_text
                            })
                        else:
                            # TODO: Log a warning for malformed metadata
                            pass
                
                retrieved_contexts[keyword] = keyword_contexts

            except Exception as e:
                # TODO: Log the error, e.g., f"Error retrieving context for keyword '{keyword}': {e}"
                # For now, return an empty list for this keyword in case of an error.
                print('ERROR QUERYING', e)
                retrieved_contexts[keyword] = []
        
        return retrieved_contexts