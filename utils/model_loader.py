import os
from typing import Any, Literal, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from utils.config_loader import load_config


class ConfigLoader:
    """Loads and manages application configuration settings.

    Provides attribute-style access to underlying configuration key-value pairs
    loaded via `load_config()`.
    """

    def __init__(self):
        """Initializes ConfigLoader and loads configuration settings."""
        print("Initializing ConfigLoader and loading configuration...")
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


class ModelLoader(BaseModel):
    """Factory for instantiating LangChain chat models based on runtime configuration."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )

    model_type: Literal["groq", "openai"] = Field(
        default="groq",
        description="Type of the language model provider to load.",
    )
    config_loader: Optional[ConfigLoader] = Field(
        default=None,
        description="Instance of ConfigLoader to access API keys and model metadata.",
    )
    
    
    def model_post_init(self):
        """Post-initialization hook to ensure config_loader is set."""
        if self.config_loader is None:
            self.config_loader = ConfigLoader()
        else:
            print("Using provided ConfigLoader instance.")
        
        

    def load_llm_model(self) -> BaseChatModel:
        """Instantiates and returns a Chat model configured for the specified provider.

        Returns:
            An instance of BaseChatModel configured for either Groq or OpenAI.

        Raises:
            ValueError: If an unsupported `model_type` is specified.
            AttributeError: If `config_loader` is None or missing required configuration keys.
        """
        if self.model_type == "groq":
            return ChatGroq(
                api_key=self.config_loader.groq_api_key,
                model_name=self.config_loader.groq_model_name,
                temperature=self.config_loader.groq_temperature,
                max_tokens=self.config_loader.groq_max_tokens,
            )
        elif self.model_type == "openai":
            return ChatOpenAI(
                api_key=self.config_loader.openai_api_key,
                model_name=self.config_loader.openai_model_name,
                temperature=self.config_loader.openai_temperature,
                max_tokens=self.config_loader.openai_max_tokens,
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")