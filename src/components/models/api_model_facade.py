import os
import time
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from components.config.model_configurations import get_model_configurations
from util.constants import ApiModelConstants
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio

class ApiModelFacade:
    """
    Facade for creating and managing API-based models using LangChain.
    """
    def __init__(self, model_name: str = None, model_type: str = "generative", api_key: str = None, temperature: float = None):
        if model_name is None:
            if model_type == "generative":
                model_name = ApiModelConstants.DEFAULT_GENERATIVE_MODEL
            elif model_type == "embedding":
                model_name = ApiModelConstants.DEFAULT_EMBEDDING_MODEL
        
        self.model_name = model_name
        self.model_type = model_type
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError(f"API key for {self.model_name} is not provided or set in environment variables.")

        self._config = self._load_model_config()
        self.llm = self._initialize_model()

    def _load_model_config(self):
        """Loads the specific model configuration."""
        all_configs = get_model_configurations()
        if self.model_type not in all_configs or self.model_name not in all_configs[self.model_type]:
            raise ValueError(f"Model '{self.model_name}' of type '{self.model_type}' not found in configuration.")
        return all_configs[self.model_type][self.model_name]

    def _initialize_model(self):
        """Initializes the LangChain model from the configuration."""
        constructor = self._config["constructor"]
        params = self._config["params"].copy()
        params["google_api_key"] = self.api_key
        if self.temperature is not None:
            params["temperature"] = self.temperature
        return constructor(**params)

    def get_chain(self) -> Runnable:
        if self.model_type != "generative":
            raise TypeError("Chains can only be created for generative models.")

        prompt_template = ChatPromptTemplate.from_messages(
            [("human", "{user_prompt}")]
        )
        return prompt_template | self.llm | StrOutputParser()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call(self, chain: Runnable, prompt: dict) -> str:
        """
        Invokes a chain with retry logic.
        """
        return chain.invoke(prompt)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def acall(self, chain: Runnable, prompt: dict) -> str:
        """
        Invokes a chain with retry logic.
        """
        try:
            return await asyncio.wait_for(chain.ainvoke(prompt), timeout=180)
        except asyncio.TimeoutError:
            # Handle timeout gracefully
            return "empty"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generates embeddings for a list of documents.
        """
        if self.model_type != "embedding":
            raise TypeError("Embedding can only be performed with embedding models.")
        return self.llm.embed_documents(texts)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def embed_query(self, text: str) -> list[float]:
        """
        Generates an embedding for a single query.
        """
        if self.model_type != "embedding":
            raise TypeError("Embedding can only be performed with embedding models.")
        return self.llm.embed_query(text)