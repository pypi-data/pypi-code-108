from base64 import b64encode, b64decode


def scramble(clear_content: str):
    return b64encode(clear_content.encode("utf-8")).decode("utf-8")


def unscramble(scrambled_content: str):
    return b64decode(scrambled_content.encode("utf-8")).decode("utf-8")
