"""LLM Service for generating responses."""

from google import genai
from google.genai import types

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """Generate responses using Google Gemini."""

    def __init__(self):
        """Initialize Google GenAI client."""

        self.client = genai.Client(
            api_key=settings.google_api_key
        )

        self.model = settings.google_llm_model

        logger.info(
            f"Initialized Google Gemini with model: {self.model}"
        )

    def generate(
        self,
        prompt: str,
        context: list[str] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a response from Gemini."""

        system_message = """
You are a helpful AI assistant answering questions based on provided context.
If the context doesn't contain relevant information, say so.
Always cite your sources when using information from the context.
""".strip()

        if context:
            context_str = "\n\n".join(context)
            system_message += f"\n\nContext:\n{context_str}"

        full_prompt = f"{system_message}\n\nUser Question: {prompt}"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            return response.text or ""

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
        """Generate a streaming response from Gemini."""

        system_message = """
You are a helpful AI assistant answering questions based on provided context.
If the context doesn't contain relevant information, say so.
Always cite your sources when using information from the context.
""".strip()

        if context:
            context_str = "\n\n".join(context)
            system_message += f"\n\nContext:\n{context_str}"

        full_prompt = f"{system_message}\n\nUser Question: {prompt}"

        try:
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            for chunk in stream:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise