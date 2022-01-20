import math
import re

ELLIPSIS = "..."
MAX_SUFFIX = 3


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate long text."""
    if not text or not max_length:
        return ""

    len_ellipsis = len(ELLIPSIS)

    text = text.replace("\r", "").replace("\n", "")

    if max_length >= len(text):
        return text
    elif len_ellipsis >= max_length:
        return text[:max_length]

    start = max_length - len_ellipsis - MAX_SUFFIX

    if start < MAX_SUFFIX:
        start = math.ceil((max_length - len_ellipsis) / 2)

    end = max_length - start - len_ellipsis

    return "{0}{1}{2}".format(
        text[:start],
        ELLIPSIS,
        text[-end:] if end > 0 else "",
    )


def camel_case_to_snack_case(text: str) -> str:
    """Convert CamelCase -> snake_case."""
    text = _validate_text(text)

    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", text).lower()


def snack_case_to_camel_case(text: str) -> str:
    """Convert snake_case -> CamelCase."""
    text = _validate_text(text)

    first, *words = text.split("_")
    return "{0}{1}".format(first, "".join(map(lambda x: x.title(), words)))


def remove_prefix(text: str, prefix: str) -> str:
    """
    Remove prefix for string.

    Obsolete with python3.9+
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def _validate_text(text: str) -> str:
    """Text validation for convert snack <-> camel cases."""
    text = text.strip()

    if re.search(r"\s", text):
        raise ValueError("The text should not contain spaces")

    return text
