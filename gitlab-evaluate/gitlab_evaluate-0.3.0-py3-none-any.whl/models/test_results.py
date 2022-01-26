from typing import List, Dict
from pydantic import BaseModel


class TestResults(BaseModel):
    programming_languages: Dict[str, bool] = {}
    multiple_build_files: Dict[str, int] = {}
    sprawling_build_files: Dict[str, int] = {}
    multiple_container_files: Dict[str, int] = {}
    sprawling_config_files: Dict[str, str] = {}
    no_stored_database_files: Dict[str, bool] = {}
    nested_build_tools: Dict[str, bool] = {}