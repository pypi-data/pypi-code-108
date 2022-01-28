#!/usr/bin/env python3

from typing import Any, Dict

import pytest


@pytest.fixture
def valid_himarc() -> Dict[str, Any]:
    return {
        "fields": {
            "222": {
                "indicator1": "\\",
                "indicator2": "0",
                "subFields": [{"a": "Nature"}, {"b": "(London)"}],
            },
            "245": {
                "indicator1": "1",
                "indicator2": "0",
                "subFields": [{"a": "Another Nature"}],
            },
            "260": [
                {
                    "indicator1": "\\",
                    "indicator2": "\\",
                    "subFields": [{"a": "Paris"}, {"b": "My Publisher"}],
                }
            ],
            "LDR": {
                "positions": {
                    "10": "2",
                    "11": "2",
                    "17": " ",
                    "18": "a",
                    "19": " ",
                    "20": "4",
                    "21": "5",
                    "22": "0",
                    "23": "0",
                    "00-04": "02105",
                    "05": "c",
                    "06": "a",
                    "07": "s",
                    "08": " ",
                    "09": "a",
                    "12-16": "00541",
                }
            },
            "008": {
                "positions": {
                    "18": "w",
                    "19": "r",
                    "20": " ",
                    "21": "p",
                    "22": " ",
                    "23": " ",
                    "24": " ",
                    "25": " ",
                    "26": " ",
                    "27": " ",
                    "28": " ",
                    "29": "0",
                    "33": "a",
                    "34": "0",
                    "38": " ",
                    "39": " ",
                    "00-05": "190816",
                    "06": "c",
                    "07-10": "1869",
                    "11-14": "9999",
                    "15-17": "enk",
                    "30-32": "   ",
                    "35-37": "eng",
                }
            },
            "022": {
                "indicator1": "0",
                "indicator2": "\\",
                "subFields": [
                    {"a": "0028-0836"},
                    {"z": "0302-2889"},
                    {"2": "_2"},
                    {"l": "0028-0836"},
                ],
            },
            "044": {
                "indicator1": "\\",
                "indicator2": "\\",
                "subFields": [{"c": "GBR"}],
            },
            "080": [
                {
                    "indicator1": "0",
                    "indicator2": "\\",
                    "subFields": [{"a": "539.120.222"}],
                }
            ],
        }
    }


@pytest.fixture
def invalid_himarc() -> Dict[str, Any]:
    return {
        "fields": {
            "222": {
                "indicator1": "\\",
                "indicator2": "0",
                "subFields": [{"a": "Nature"}, {"b": "(London)"}],
            },
            "245": {
                "indicator1": "1",
                "indicator2": "0",
                "subFields": [{"a": "Another Nature"}],
            },
            "260": [
                {
                    "indicator1": "\\",
                    "indicator2": "\\",
                    "subFields": [{"a": "Paris"}, {"b": "My Publisher"}],
                }
            ],
            "LDR": {
                "positions": {
                    "18": "a",
                    "19": " ",
                    "20": "4",
                    "21": "5",
                    "22": "0",
                    "23": "0",
                    "00-04": "02105",
                    "05": "c",
                    "06": "a",
                    "07": "s",
                    "08": " ",
                    "09": "a",
                    "12-16": "00541",
                }
            },
            "008": {
                "positions": {
                    "18": "w",
                    "19": "r",
                    "20": " ",
                    "21": "p",
                    "22": " ",
                    "23": " ",
                    "24": " ",
                    "25": " ",
                    "26": " ",
                    "27": " ",
                    "28": " ",
                    "29": "0",
                    "33": "a",
                    "34": "0",
                    "38": " ",
                    "39": " ",
                    "00-05": "190816",
                    "06": "c",
                    "07-10": "1869",
                    "11-14": "9999",
                    "15-17": "enk",
                    "30-32": "   ",
                    "35-37": "eng",
                }
            },
            "022": {
                "indicator1": "0",
                "indicator2": "\\",
                "subFields": [
                    {"a": "0028-0836"},
                    {"z": "0302-2889"},
                    {"2": "_2"},
                    {"l": "0028-0836"},
                ],
            },
            "044": {
                "indicator1": "\\",
                "indicator2": "\\",
                "subFields": [{"c": "GBRA"}],
            },
            "080": [
                {
                    "indicator1": "0",
                    "indicator2": "\\",
                    "subFields": [{"a": "539.120.222"}],
                }
            ],
        }
    }


@pytest.fixture
def empty_dict() -> Dict[str, Any]:
    return {}
