from __future__ import annotations

import json
from functools import cached_property
from typing import Any

from openai import OpenAI

from app.config import Settings, get_settings


class OpenAIConfigurationError(RuntimeError):
    """Raised when OpenAI provider settings are incomplete."""


class OpenAIResponsesClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.openai_api_key)

    @cached_property
    def _client(self) -> OpenAI:
        if not self.settings.openai_api_key:
            raise OpenAIConfigurationError(
                "OPENAI_API_KEY is required before calling the OpenAI Responses API."
            )

        return OpenAI(api_key=self.settings.openai_api_key)

    def create_json_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        json_schema: dict[str, Any],
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model or self.settings.openai_model,
            "input": build_text_input(system_prompt=system_prompt, user_prompt=user_prompt),
            "reasoning": {"effort": self.settings.openai_reasoning_effort},
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": json_schema,
                    "strict": True,
                }
            },
        }
        if tools:
            payload["tools"] = tools

        response = self._client.responses.create(**payload)
        return json.loads(extract_output_text(response))

    def create_text_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self.settings.openai_model,
            "input": build_text_input(system_prompt=system_prompt, user_prompt=user_prompt),
            "reasoning": {"effort": self.settings.openai_reasoning_effort},
        }
        if tools:
            payload["tools"] = tools

        response = self._client.responses.create(**payload)
        return extract_output_text(response)


def build_text_input(*, system_prompt: str, user_prompt: str) -> list[dict[str, Any]]:
    return [
        {
            "role": "system",
            "content": [{"type": "input_text", "text": system_prompt}],
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": user_prompt}],
        },
    ]


def extract_output_text(response: Any) -> str:
    direct_text = getattr(response, "output_text", None)
    if isinstance(direct_text, str) and direct_text:
        return direct_text

    output_items = getattr(response, "output", None)
    if isinstance(output_items, list):
        text_parts: list[str] = []
        for item in output_items:
            content_items = getattr(item, "content", None)
            if not isinstance(content_items, list):
                continue
            for content in content_items:
                text = getattr(content, "text", None)
                if isinstance(text, str) and text:
                    text_parts.append(text)
        if text_parts:
            return "\n".join(text_parts)

    raise RuntimeError("OpenAI response did not contain readable text output.")
