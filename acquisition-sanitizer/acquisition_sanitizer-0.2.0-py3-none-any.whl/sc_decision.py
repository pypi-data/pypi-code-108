from html_sanitizer import Sanitizer
from html_sanitizer.sanitizer import (
    bold_span_to_strong,
    italic_span_to_em,
    sanitize_href,
    tag_replacer,
    target_blank_noopener,
)

case_sanitizer = Sanitizer(
    {
        "tags": {
            "a",
            "h1",
            "h2",
            "h3",
            "strong",
            "center",
            "em",
            "p",
            "ul",
            "ol",
            "li",
            "br",
            "blockquote",
            "sub",
            "sup",
            "hr",
            "table",
            "td",
            "tr",
        },
        "attributes": {
            "p": ("align"),
            "a": ("href", "name", "target", "title", "id", "rel"),
            "sup": ("id"),
        },
        "empty": {"hr", "a", "br"},
        "separate": {"a", "p", "li"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": True,
        "add_nofollow": False,
        "autolink": False,
        "sanitize_href": sanitize_href,
        "element_preprocessors": [
            bold_span_to_strong,
            italic_span_to_em,
            tag_replacer("b", "strong"),
            tag_replacer("i", "em"),
            tag_replacer("form", "p"),
            target_blank_noopener,
        ],
        "element_postprocessors": [],
        "is_mergeable": lambda e1, e2: True,
    }
)
