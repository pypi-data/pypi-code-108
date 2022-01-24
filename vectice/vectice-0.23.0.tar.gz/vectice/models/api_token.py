from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import logging
import json


@dataclass
class ApiToken:
    name: Optional[str] = None
    description: Optional[str] = None
    key: str = ""

    @staticmethod
    def parse_api_token_json(token_file: str) -> ApiToken:
        logging.info("Parsing api token json file...")
        with open(token_file) as file:
            data = json.load(file)
        return ApiToken(**data)
