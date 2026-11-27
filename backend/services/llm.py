"""Shared access to the Groq LLM client.

The client is created lazily so the app (and the test suite) can start without
a ``GROQ_API_KEY``. When no key is configured the services fall back to
deterministic heuristics ("demo mode"), so the whole stack can be tried
locally or in a hosted demo without spending tokens.
"""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Any

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TRANSCRIBE_MODEL = os.getenv("GROQ_TRANSCRIBE_MODEL", "whisper-large-v3")


@lru_cache(maxsize=1)
def get_client():
    """Return a Groq client, or ``None`` when running in demo mode."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    from groq import Groq

    return Groq(api_key=api_key)


def demo_mode() -> bool:
    return get_client() is None


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(content: str) -> dict[str, Any]:
    """Parse a JSON object out of an LLM reply.

    Models sometimes wrap JSON in Markdown fences or add a sentence around it,
    so try the fenced block first, then the outermost ``{...}`` span.
    """
    match = _FENCE.search(content)
    if match:
        content = match.group(1)
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(content[start : end + 1])


def chat_completion(messages: list[dict[str, str]], *, temperature: float, max_tokens: int) -> str:
    client = get_client()
    if client is None:  # pragma: no cover - callers check demo_mode() first
        raise RuntimeError("GROQ_API_KEY is not set")
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""
