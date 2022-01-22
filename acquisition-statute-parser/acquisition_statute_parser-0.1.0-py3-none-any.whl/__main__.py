from typing import Optional

from .demarcator import get_demarcated_data
from .sanitizer import statute_sanitizer
from .setter import cull_footer, set_data


def parse(raw: str, context: str) -> Optional[dict]:
    """Parsed the raw text under a given context, e.g. "ra", "pd", etc.
    The footer needs to be culled from the raw text.
    The raw text needs to be demarcated, depending on the context.
    The demarcated text needs to be split.
    The resulting data dictionary is based on the text demarcated.

    Args:
        raw (str): stringified HTML markup
        context (str): determines demarcations for slicing the raw text

    Returns:
        dict: Results of demarcated splits and culling
    """
    sanitized = statute_sanitizer.sanitize(raw)
    culled = cull_footer(sanitized)
    demarcated = get_demarcated_data(culled, context)
    data = set_data(demarcated)
    return data
