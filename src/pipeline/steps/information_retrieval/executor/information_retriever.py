# src/components/agents/information_retriever.py
"""
InformationRetriever agent for extracting keywords, phrases, and relevant context.
"""
import json
from typing import Dict, List, Any

from common.config.config_helper import ConfigurationHelper
from components.models.embedding_model_facade import HuggingFaceEmbeddingFacade
from infrastructure.vector_db.chroma_client import ChromaClient
from prompts.keyword_phrases_extraction import PROMPT, FEW_SHOT_EXAMPLES_FOR_DICT_OUTPUT_STR
from util.constants import PreprocessingConstants
from util.db.database_descriptor import DatabaseDescriptor, TableDescriptor, ColumnDefinition
from executor.task_model import Task
from util.similarity_measures.lsh import LSHUtil
from util.similarity_measures.semantic import SemanticSimilarityUtil
from util.similarity_measures.edit import EditDistanceUtil
from components.models.api_model_facade import ApiModelFacade
from util.similarity_measures.bm25 import BM25Util
from components.models.reranker_facade import Reranker

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
        # self.reasoning_model = ReasoningModelFacade(model_name=reasoning_model_name)
        self.api_model = ApiModelFacade(temperature=0.8)

        # Initialize ConfigurationHelper to load ChromaDB settings
        self.config_helper = ConfigurationHelper()
        chroma_config = self.config_helper.get_config('chroma_db.yaml', 'chroma_db')

        chroma_host = chroma_config.get('host', PreprocessingConstants.DEFAULT_CHROMA_HOST)
        chroma_port = chroma_config.get('port', PreprocessingConstants.DEFAULT_CHROMA_PORT)

        # Initialize Embedding Facade
        self.embedding_facade = HuggingFaceEmbeddingFacade()

        # Initialize ChromaClient
        self.chroma_client = ChromaClient(
            host=chroma_host,
            port=chroma_port,
            embedding_facade=self.embedding_facade
        )

        # Store collection name
        self.column_collection_name = PreprocessingConstants.COLUMN_COLLECTION_NAME
        self.semantic_similarity_util = SemanticSimilarityUtil()
        self.bm25_retrievers = {}
        self.reranker = Reranker()


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
            query_chain = self.api_model.get_chain()
            response_text = self.api_model.invoke_chain(query_chain, {"user_prompt": formatted_prompt})
            print(f"LLM Unparsed Response for keyword extraction: {response_text}")
            # Expecting the LLM to output a JSON string representing a dictionary.
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            parsed_response = json.loads(response_text.strip())

            if isinstance(parsed_response, dict):
                keywords = parsed_response.get("keywords", [])
                phrases = parsed_response.get("phrases", [])

                if isinstance(keywords, list) and all(isinstance(kw, str) for kw in keywords):
                    keywords_list = [kw.strip() for kw in keywords if kw.strip()]
                else:
                    print(f"WARNING: The keyword extraction response does not contain a list for 'keywords' key")
                
                if isinstance(phrases, list) and all(isinstance(ph, str) for ph in phrases):
                    phrases_list = [ph.strip() for ph in phrases if ph.strip()]
                else:
                    print(f"WARNING: The keyword extraction response does not contain a list for 'phrases' key")
            else:
                print(f"WARNING: The keyword extraction failed. No dictionary returned.")


        except json.JSONDecodeError as e:
            print(f"ERROR: Error parsing the json: {str(e)}")
        except Exception as e:
            print(f"Error extracting the keywords: {str(e)}" )
        return {"keywords": keywords_list, "phrases": phrases_list}

    def retrieve_entities(self, db_id: str, keywords: List[str], phrases: List[str]) -> DatabaseDescriptor:
        """
        Retrieves relevant entities (tables and columns) based on keywords and phrases.

        Args:
            db_id: The ID of the database.
            keywords: A list of keywords extracted from the user query.
            phrases: A list of phrases (potential data values) from the user query.

        Returns:
            A DatabaseDescriptor object containing the relevant tables and columns.
        """
        lsh = LSHUtil.load_lsh_index(db_id)
        minhashes = LSHUtil.load_minhashes(db_id)
        
        entities_db_descriptor = DatabaseDescriptor(db_id=db_id)
        
        for keyword in phrases:
            similar_values = LSHUtil.query_lsh(lsh, minhashes, keyword)
            
            all_candidates = []
            for table_name, columns in similar_values.items():
                for column_name, values in columns.items():
                    for value in values:
                        all_candidates.append({
                            "value": value,
                            "table_name": table_name,
                            "column_name": column_name
                        })

            # Get top-n most similar candidates using edit distance
            edit_distance_candidates = EditDistanceUtil.get_top_n_similar(
                keyword,
                all_candidates,
                top_n=50
            )

            # Rerank using semantic similarity
            top_candidates = self.semantic_similarity_util.get_top_n_similar(
                keyword,
                edit_distance_candidates,
                top_n=10
            )

            # Create a new DatabaseDescriptor with the relevant entities
            for candidate in top_candidates:
                table_name = candidate["table_name"]
                column_name = candidate["column_name"]
                
                if table_name not in entities_db_descriptor.tables:
                    entities_db_descriptor.tables[table_name] = TableDescriptor(table_name=table_name)
                
                if column_name not in entities_db_descriptor.tables[table_name].columns:
                    # We don't have the full column definition here, so we create a partial one
                    entities_db_descriptor.tables[table_name].columns[column_name] = ColumnDefinition(
                        original_column_name=column_name,
                        column_name=column_name
                    )
                    
        return entities_db_descriptor

    def retrieve_context(self, keywords: List[str], task: Task, k: int = 10) -> Dict[str, List[Dict[str, Any]]]:
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

        # Load BM25 retriever if not already loaded
        if task.db_id not in self.bm25_retrievers:
            self.bm25_retrievers[task.db_id] = BM25Util.load_bm25_retriever(task.db_id)
        
        bm25_retriever = self.bm25_retrievers[task.db_id]

        for keyword in keywords:
            if not keyword.strip(): # Skip empty or whitespace-only keywords
                retrieved_contexts[keyword] = []
                continue
            try:
                # Retrieve from ChromaDB
                collection_name = f"{PreprocessingConstants.COLUMN_COLLECTION_NAME}_{task.db_id}"
                query_results = self.chroma_client.query_collection(
                    collection_name=collection_name,
                    query_texts=[keyword],
                    n_results=k * 2# Retrieve more to rerank
                )

                chroma_contexts: List[Dict[str, Any]] = []
                if query_results and query_results.get("documents") and query_results.get("metadatas"):
                    docs_for_keyword = query_results["documents"][0] if query_results["documents"] else []
                    metadatas_for_keyword = query_results["metadatas"][0] if query_results["metadatas"] else []

                    for doc_text, metadata in zip(docs_for_keyword, metadatas_for_keyword):
                        if metadata and 'column_name' in metadata and 'table_name' in metadata:
                            chroma_contexts.append({
                                "column_name": metadata['column_name'],
                                "table_name": metadata['table_name'],
                                "description": doc_text,
                                "type": metadata.get('type')
                            })

                # Rerank using BM25
                if chroma_contexts:
                    bm25_results = bm25_retriever.get_relevant_documents(keyword)
                    
                    # Combine and rerank
                    combined_results = chroma_contexts
                    chroma_keys = set((item['table_name'], item['column_name']) for item in chroma_contexts)

                    for doc in bm25_results:
                        key = (doc.metadata['table_name'], doc.metadata['column_name'])
                        if key not in chroma_keys:
                            combined_results.append({
                                "column_name": doc.metadata['column_name'],
                                "table_name": doc.metadata['table_name'],
                                "description": doc.page_content,
                                "type": doc.metadata['type']
                            })
                    
                    # Deduplicate before reranking, prioritizing by type
                    priority = {"column_description": 1, "column_name": 2, "value_description": 3}
                    seen_columns = {}
                    for item in combined_results:
                        key = (item['table_name'].lower(), item['column_name'].lower())
                        item_priority = priority.get(item.get('type'), 4)

                        if key not in seen_columns or item_priority < seen_columns[key]['priority']:
                            seen_columns[key] = {'item': item, 'priority': item_priority}
                    
                    deduplicated_results = [value['item'] for value in seen_columns.values()]

                    # Rerank with ColBERT
                    retrieved_contexts[keyword] = self.reranker.rerank(keyword, deduplicated_results, k)
                else:
                    retrieved_contexts[keyword] = []

            except Exception as e:
                print(f"Error retrieving context for keyword '{keyword}': {str(e)}")
                retrieved_contexts[keyword] = []
        
        return retrieved_contexts