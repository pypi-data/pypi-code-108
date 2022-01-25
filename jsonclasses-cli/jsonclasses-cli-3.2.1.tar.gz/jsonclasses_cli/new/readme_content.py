from pathlib import Path


def readme_content(dest: Path) -> str:
    return f"""
{dest.name}
========

This project is created with JSONClasses CLI.
    """.strip() + '\n'
