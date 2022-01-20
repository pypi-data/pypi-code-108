import re
import subprocess
import tempfile
from typing import List

from bqq import const
from rich.text import Text


def color_keywords(query: str) -> Text:
    text = Text(query)
    words = "|".join(const.BQ_KEYWORDS)
    regex = re.compile(f"^({words})|(\s+({words})\s+)", re.IGNORECASE)  # match keywords
    text.highlight_regex(regex, const.keyword_style)
    return text


def fzf(choices: List[str], multi=False, key=None) -> List[str]:
    choices.sort(reverse=True, key=key)
    choices_str = "\n".join(map(str, choices))
    selection = []
    multi = "--multi" if multi else None
    fzf_args = filter(None, ["fzf", "--ansi", multi])
    with tempfile.NamedTemporaryFile() as input_file:
        with tempfile.NamedTemporaryFile() as output_file:
            input_file.write(choices_str.encode("utf-8"))
            input_file.flush()
            cat = subprocess.Popen(["cat", input_file.name], stdout=subprocess.PIPE)
            subprocess.run(fzf_args, stdin=cat.stdout, stdout=output_file)
            cat.wait()
            with open(output_file.name) as f:
                selection = [line.strip("\n") for line in f.readlines()]
    return selection
