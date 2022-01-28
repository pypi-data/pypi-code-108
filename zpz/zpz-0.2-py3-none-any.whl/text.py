def isascii(text: str) -> bool:
    return len(text) == len(text.encode())
