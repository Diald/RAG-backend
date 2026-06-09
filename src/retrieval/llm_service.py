"""LLM Service for generating responses."""

import logging

from google import genai

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """Generate responses using Google Gemini."""

    def __init__(self):
        """Initialize Google Gemini client."""
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.google_llm_model
        logger.info(f"Initialized Google Gemini with model: {self.model}")

    def generate(
        self,
        prompt: str,
        context: list[str] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a response from Gemini.

        Args:
            prompt: User prompt
            context: Optional context documents
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response
        """
        system_message = """You are a helpful AI assistant answering questions based on provided context.
If the context doesn't contain relevant information, say so.
Always cite your sources when using information from the context."""

        if context:
            context_str = "\n\n".join(context)
            system_message += f"\n\nContext:\n{context_str}"

        full_prompt = f"{system_message}\n\nUser Question: {prompt}"

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            model = genai.GenerativeModel(
                self.model,
                generation_config=generation_config,
            )
            
            response = model.generate_content(full_prompt)
            return response.text

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
        """Generate a streaming response from Gemini.

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

        full_prompt = f"{system_message}\n\nUser Question: {prompt}"

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            model = genai.GenerativeModel(
                self.model,
                generation_config=generation_config,
            )
            
            stream = model.generate_content(full_prompt, stream=True)
            
            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise
