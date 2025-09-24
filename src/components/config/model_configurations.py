from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

def get_model_configurations():
    """
    Returns a dictionary of model configurations, separated by type.
    Each configuration includes the model constructor and default parameters.
    """
    return {
        "generative": {
            "gemini-2.5-pro": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-2.5-pro",
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            },
            "gemini-2.5-flash": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-2.5-flash",
                    "temperature": 0.5,
                }
            },
            "gemini-2.5-flash-lite": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-2.5-flash-lite",
                    "temperature": 0.5,
                }
            },
            "gemini-2.0-flash": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-2.0-flash",
                    "temperature": 0.5,
                }
            },
            "gemini-2.0-flash-lite": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-2.0-flash-lite",
                    "temperature": 0.5,
                }
            },
            "gemini-1.5-flash": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-1.5-flash",
                    "temperature": 0.5,
                }
            },
            "gemini-1.5-pro": {
                "constructor": ChatGoogleGenerativeAI,
                "params": {
                    "model": "gemini-1.5-pro",
                    "temperature": 0.7,
                }
            },
        },
        "embedding": {
            "gemini-embedding-001": {
                "constructor": GoogleGenerativeAIEmbeddings,
                "params": {
                    "model": "gemini-embedding-001",
                }
            }
        }
    }