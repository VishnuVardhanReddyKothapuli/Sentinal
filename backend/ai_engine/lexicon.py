"""Small transparent safety rules, configurable with SENTINEL_TEXT_LEXICON."""

import os
import re
import unicodedata

# Comma-separated deployment configuration replaces this deliberately limited list.
DEFAULT_TERMS = ("kill yourself", "kill all", "white power", "heil hitler", "fuck", "shit")


def evaluate_text(text: str) -> tuple[bool, str | None]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    configured = os.getenv("SENTINEL_TEXT_LEXICON")
    terms = configured.split(",") if configured is not None else DEFAULT_TERMS
    hits = []
    for term in terms:
        term = unicodedata.normalize("NFKC", term.strip()).casefold()
        if not term:
            continue
        expression = r"(?<!\w)" + r"\s+".join(re.escape(piece) for piece in term.split()) + r"(?!\w)"
        if re.search(expression, normalized):
            hits.append(term)
    return bool(hits), "Configured text safety terms detected: " + ", ".join(hits) if hits else None
