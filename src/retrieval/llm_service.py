"""LLM Service for generating responses."""

import logging
from typing import Any

from openai import OpenAI
from groq import Groq

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """Generate responses using OpenAI or Groq."""

    def __init__(self):
        """Initialize LLM client based on configuration."""
        self.provider = settings.get_llm_provider()

        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        else:
            self.client = Groq(api_key=settings.groq_api_key)
            self.model = settings.groq_model

    def generate(
        self,
        prompt: str,
        context: list[str] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: User prompt
            context: Optional context documents
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response
        """
        # Build system message with context
        system_message = """You are a helpful AI assistant answering questions based on provided context.
        If the context doesn't contain relevant information, say so.
        Always cite your sources when using information from the context."""

        if context:
            context_str = "\n\n".join(context)
            system_message += f"\n\nContext:\n{context_str}"

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def stream_generate(
        self,
        prompt: str,
        context: list[str] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """Generate a streaming response from the LLM.

        Args:
            prompt: User prompt
            context: Optional context documents
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response chunks
        """
        system_message = """You are a helpful AI assistant answering questions based on provided context.
        If the context doesn't contain relevant information, say so.
        Always cite your sources when using information from the context."""

        if context:
            context_str = "\n\n".join(context)
            system_message += f"\n\nContext:\n{context_str}"

        try:
            if self.provider == "openai":
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise
