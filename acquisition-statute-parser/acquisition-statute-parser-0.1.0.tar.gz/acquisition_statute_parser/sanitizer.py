from html_sanitizer import Sanitizer
from html_sanitizer.sanitizer import (
    italic_span_to_em,
    sanitize_href,
    tag_replacer,
    target_blank_noopener,
)

statute_sanitizer = Sanitizer(
    {
        "tags": {
            "h2",
            "h3",
            "em",
            "center",
            "p",
            "ul",
            "ol",
            "li",
            "br",
            "blockquote",
            "hr",
            "table",
            "tbody",
            "td",
            "tr",
        },
        "attributes": {"p": ("id", "data-type")},
        "empty": {"br", "hr"},
        "separate": {"p", "li"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": False,
        "add_nofollow": False,
        "autolink": False,
        "sanitize_href": sanitize_href,
        "element_preprocessors": [
            italic_span_to_em,
            tag_replacer("i", "em"),
            tag_replacer("span", "p"),
            tag_replacer("font", "p"),
            target_blank_noopener,
        ],
        "element_postprocessors": [],
        "is_mergeable": lambda e1, e2: True,
    }
)  # preconfigure settings
