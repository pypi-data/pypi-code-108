def gitignore_content() -> str:
    return """
# packages
/packages

# python
__pycache__

# venv
venv
.venv

# dotenv
.env

# mypy
.mypy_cache

# vscode
.vscode

# idea
.idea
*.iml
    """.strip() + '\n'
