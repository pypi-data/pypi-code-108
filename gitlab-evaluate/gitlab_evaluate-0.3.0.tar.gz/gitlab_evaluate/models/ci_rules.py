from typing import List
from pydantic import BaseModel


class CiRules(BaseModel):
    languages: List[str] = []
    build_dependencies: List[str] = []
    database_filetypes: List[str] = []
    container_filetypes: List[str] = []
    config_filetypes: List[str] = []
    build_command_snippets: List[str] = []
