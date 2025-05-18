# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from os import getenv
from typing import get_args

from openai import OpenAI

from Backend.utility.error.common import EnvironmentVariableNotSetError
from Backend.utility.error.llm.llm import InvalidOpenAIChatModelError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.llm import OPENAI_CHAT_MODEL_LIST

from .prompt import SEARCH_PROMPT, SUMMARY_PROMPT


class LLMResponser:
    def __init__(
        self,
        openai_api_key: str | None = None,
        openai_embedding_model: str = "",
        openai_chat_model: OPENAI_CHAT_MODEL_LIST | None = None,
    ) -> None:
        self.logger = Logger().get_logger()
        self.client = OpenAI()

        self._openai_api_key = openai_api_key if openai_api_key else getenv("OPENAI_API_KEY")
        self._openai_embedding_model = (
            openai_embedding_model if openai_embedding_model else getenv("OPENAI_EMBEDDING_MODEL")
        )
        self._openai_chat_model = openai_chat_model if openai_chat_model else getenv("OPENAI_CHAT_MODEL")

        if self._openai_api_key is None:
            msg = "OPENAI_API_KEY"
            raise EnvironmentVariableNotSetError(msg)

        if self._openai_embedding_model is None:
            msg = "OPENAI_EMBEDDING_MODEL"
            raise EnvironmentVariableNotSetError(msg)

        self.client.api_key = self._openai_api_key

    def search_response(
        self,
        query: str,
        max_tokens: int = 8192,
        temperature: float = 0.6,
        top_p: int = 1,
        frequence_penalty: int = 1,
    ) -> tuple[str, int]:
        if self._openai_chat_model is None:
            msg = "OPENAI_CHAT_MODEL"
            raise EnvironmentVariableNotSetError(msg)

        if self._openai_chat_model not in get_args(OPENAI_CHAT_MODEL_LIST):
            raise InvalidOpenAIChatModelError(self._openai_chat_model)

        response = self.client.chat.completions.create(
            model=self._openai_chat_model,
            messages=[
                {"role": "system", "content": SEARCH_PROMPT},
                {
                    "role": "user",
                    "content": query,
                },
            ],
            frequency_penalty=frequence_penalty,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        response_dump = response.model_dump(mode="python")

        self.logger.debug(response_dump)

        if not response:
            self.logger.error("Failed to generate OpenAI response")
            return "", 0

        token_count = response_dump["usage"]["total_tokens"] or 0
        message_dump = response.choices[0].message.model_dump(mode="python")

        return str(message_dump["content"]), token_count

    def summary_response(
        self,
        query: str,
        max_tokens: int = 8192,
        temperature: float = 0.6,
        top_p: int = 1,
        frequence_penalty: int = 1,
    ) -> tuple[str, int]:
        if self._openai_chat_model is None:
            msg = "OPENAI_CHAT_MODEL"
            raise EnvironmentVariableNotSetError(msg)

        if self._openai_chat_model not in get_args(OPENAI_CHAT_MODEL_LIST):
            raise InvalidOpenAIChatModelError(self._openai_chat_model)

        response = self.client.chat.completions.create(
            model=self._openai_chat_model,
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {
                    "role": "user",
                    "content": query,
                },
            ],
            frequency_penalty=frequence_penalty,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        response_dump = response.model_dump(mode="python")

        self.logger.debug(response_dump)

        if not response:
            self.logger.error("Failed to generate OpenAI response")
            return "", 0

        token_count = response_dump["usage"]["total_tokens"] or 0
        message_dump = response.choices[0].message.model_dump(mode="python")

        return str(message_dump["content"]), token_count

    def embed_text(self, text: str) -> list[float]:
        """
        Encode the input text into a vector embedding using OpenAI's API.

        This method sends the input text to OpenAI's embedding service and returns
        the resulting vector representation.

        Args:
            text (str): The input text to be encoded into a vector embedding.

        Returns:
            list[float]: A list of floats representing the vector embedding of the input text.

        Raises:
            Exception: If there's an error in calling the OpenAI API or processing the response.

        """
        if self._openai_embedding_model is None:
            msg = "OPENAI_EMBEDDING_MODEL"
            raise EnvironmentVariableNotSetError(msg)

        response = self.client.embeddings.create(
            model=self._openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding


if __name__ == "__main__":
    ...
