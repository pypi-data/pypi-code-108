import re

__all__ = [
    'parse',
]

TOKENIZER = re.compile(r'[\s;,]+|(?<!\w)|(?!\w)')
INITIAL_TOKEN = '<START>'
FINAL_TOKEN = '<END>'


def parse(code: str) -> list[str]:
    return (
        [INITIAL_TOKEN]
        + [token for token in re.split(TOKENIZER, code) if token]
        + [FINAL_TOKEN]
    )
