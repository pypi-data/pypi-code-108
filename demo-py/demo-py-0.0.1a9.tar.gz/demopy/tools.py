import re

def clean_multiline_str(s: str):
    return re.sub(
        #     |||||| <- Clear comments too.
        r"^\s*('.*)?", 
        "",
        s.strip(),
        flags=re.M
    )