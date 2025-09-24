import os
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from components.config.model_configurations import get_model_configurations
from util.constants import ApiModelConstants

class ApiModelFacade:
    """
    Facade for creating and managing API-based models using LangChain.
    """
    def __init__(self, model_name: str = None, model_type: str = "generative", api_key: str = None):
        if model_name is None:
            if model_type == "generative":
                model_name = ApiModelConstants.DEFAULT_GENERATIVE_MODEL
            elif model_type == "embedding":
                model_name = ApiModelConstants.DEFAULT_EMBEDDING_MODEL
        
        self.model_name = model_name
        self.model_type = model_type
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
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
        return constructor(**params)

    def get_chain(self, user_prompt: str = None) -> Runnable:
        """
        Creates and returns a LangChain runnable (chain) for the model.
        """
        if self.model_type != "generative":
            raise TypeError("Chains can only be created for generative models.")

        messages = []
        if user_prompt:
            messages.append(("human", user_prompt))
        
        prompt_template = ChatPromptTemplate.from_messages(messages)
        return prompt_template | self.llm | StrOutputParser()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generates embeddings for a list of documents.
        """
        if self.model_type != "embedding":
            raise TypeError("Embedding can only be performed with embedding models.")
        return self.llm.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """
        Generates an embedding for a single query.
        """
        if self.model_type != "embedding":
            raise TypeError("Embedding can only be performed with embedding models.")
        return self.llm.embed_query(text)