"""Application configuration from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """OpenAI API configuration loaded from .env file."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def validate(self) -> None:
        """Ensure OPENAI_API_KEY is configured."""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not set in .env file. "
                "See .env.example for configuration template."
            )

    def get_llm(self):
        """Return configured ChatOpenAI LLM instance."""
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.openai_model,
            api_key=self.openai_api_key,
            temperature=0.7,
        )


settings = Settings()
