import os
from typing import Any, Literal, Optional
from dotenv import load_dotenv
import pydantic.main

# --- RUNTIME MONKEY PATCH FOR PYDANTIC / LANGCHAIN INCOMPATIBILITY ---
_original_model_post_init = pydantic.main.BaseModel.model_post_init

def _patched_model_post_init(self, *args, **kwargs):
    # Safely handle both positional context and keyword arguments
    try:
        return _original_model_post_init(self, *args, **kwargs)
    except TypeError:
        # Fallback if Pydantic signature differs across micro-versions
        return _original_model_post_init(self)

pydantic.main.BaseModel.model_post_init = _patched_model_post_init
# ---------------------------------------------------------------------

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from utils.config_loader import load_config
from logger.logging import get_logger

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__name__)


class ConfigLoader:
    """Loads and manages application configuration settings.

    Provides attribute-style access to underlying configuration key-value pairs
    loaded via `load_config()`.
    """

    def __init__(self):
        """Initializes ConfigLoader and loads configuration settings."""
        logger.debug("Initializing ConfigLoader and loading configuration...")
        self.config = load_config()

    def __getattr__(self, key: str) -> Any:
        """Retrieves configuration values as attributes.

        Args:
            key: The configuration parameter name to access.

        Returns:
            The value associated with the specified key in the configuration dictionary.

        Raises:
            AttributeError: If the key is not present in the configuration.
        """
        if key in self.config:
            return self.config[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")


class ModelLoader:
    """Factory for instantiating LangChain chat models based on runtime configuration."""

    def __init__(
        self,
        model_provider: Literal["groq", "openai"] = "groq",
        config_loader: Optional[ConfigLoader] = None,
    ):
        self.model_provider = model_provider
        self.config_loader = config_loader or ConfigLoader()
        logger.debug("ModelLoader initialized.")

    def load_llm_model(self) -> BaseChatModel:
        """Instantiates and returns a Chat model configured for the specified provider.

        Returns:
            An instance of BaseChatModel configured for either Groq or OpenAI.

        Raises:
            ValueError: If an unsupported `model_provider` is specified.
            AttributeError: If `config_loader` is None or missing required configuration keys.
        """
        provider_cfg = self.config_loader.llm[self.model_provider]
        model_name = provider_cfg["model_name"]
        
        # Strip provider prefix if present (e.g., 'groq/compound' -> 'compound')
        if "/" in model_name:
            model_name = model_name.split("/")[-1]

        temperature = provider_cfg.get("temperature", 0.7)
        max_tokens = provider_cfg.get("max_tokens", 1000)

        logger.debug(f"Model Name: {model_name} | Temperature: {temperature} | Max Tokens: {max_tokens}")

        if self.model_provider == "groq":
            logger.debug(f"Creating {self.model_provider} LLM Instance with Model: {model_name}")
            llm_model = ChatGroq(
                api_key=os.environ.get("GROQ_API_KEY"),
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif self.model_provider == "openai":
            logger.debug(f"Creating {self.model_provider} LLM Instance with Model: {model_name}")
            llm_model = ChatOpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_provider}")

        logger.debug(f"Successfully loaded model instance**")
        return llm_model