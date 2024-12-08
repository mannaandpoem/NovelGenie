from typing import Optional

import openai
from pydantic import BaseModel, Field, model_validator

from novel_genie.config import LLMSettings, config
from novel_genie.prompts.system_prompt import SYSTEM_PROMPT
from novel_genie.utils import filter_thinking_blocks


class LLM(BaseModel):
    config: LLMSettings = Field(...)
    model: str = Field(...)
    api_key: str = Field(...)
    base_url: Optional[str] = Field(None)
    max_tokens: int = Field(1000)
    temperature: float = Field(0.7)

    @model_validator(mode="after")
    def initialize_openai(self) -> "LLM":
        openai.api_key = self.api_key
        if self.base_url:
            openai.api_base = self.base_url
        return self

    def __init__(self, llm_config: Optional[LLMSettings] = None, **data):
        if llm_config is None:
            llm_config = config.llm

        super().__init__(
            config=llm_config,
            model=llm_config.model,
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            max_tokens=llm_config.max_tokens,
            temperature=llm_config.temperature,
            **data
        )

    @filter_thinking_blocks()
    async def ask(
        self, prompt: str, stream: bool = True, system_prompt: str = SYSTEM_PROMPT
    ) -> str:
        """
        Send a prompt to the LLM and get the response.

        Args:
            prompt (str): The prompt to send
            stream (bool): Whether to stream the response
            system_prompt (str): The system prompt to send

        Returns:
            str: The generated response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=stream,
        )

        if not stream:
            return response["choices"][0]["message"]["content"].strip()

        # Handle streaming response
        collected_chunks = []
        collected_messages = []

        async for chunk in response:
            collected_chunks.append(chunk)  # save the chunk
            chunk_message = chunk["choices"][0].get("delta", {}).get("content", "")
            collected_messages.append(chunk_message)

            # Print the chunk directly to console
            print(chunk_message, end="", flush=True)

        print()
        return "".join(collected_messages).strip()
