import black


def reformat_code_str(code_str: str) -> str:
    return black.format_str(code_str, mode=black.Mode(line_length=110))
