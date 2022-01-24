def mypy_content() -> str:
    return """
[mypy]
plugins = jsonclasses.mypy
    """.strip() + '\n'
