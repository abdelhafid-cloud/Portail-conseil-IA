from __future__ import annotations

from typing import Any


def summarize_conversation(messages: list[dict[str, Any]]) -> str:
    if not messages:
        return 'No prior conversation history.'

    highlights = []
    for message in messages[-5:]:
        content = str(message.get('content', '')).strip()
        if content:
            highlights.append(content[:120])

    return ' | '.join(highlights)
