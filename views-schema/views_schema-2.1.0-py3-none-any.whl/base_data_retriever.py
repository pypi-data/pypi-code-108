"""
views_schema.base_data_retriever
================================

This module exposes a data model for levels of analysis, as well as a set of
default LOAs that can be requested without having to define them in the
database.

attributes:
    LevelOfAnalysis:            A pydantic class for communicating levels of analysis
    DEFAULT_LEVELS_OF_ANALYSIS: A dictionary of default levels of analysis

"""
from pydantic import BaseModel

class LevelOfAnalysis(BaseModel):
    name: str
    description: str
    time_index: str
    unit_index: str

DEFAULT_LEVELS_OF_ANALYSIS = {
    "priogrid_month":{
        "index_columns":[
                "month_id",
                "priogrid_gid",
            ],
    },
    "priogrid_year":{
        "index_columns":[
                "year_id",
                "priogrid_gid",
            ],
    },

    "country_month":{
        "index_columns":[
                "month_id",
                "country_id",
            ],
    },
    "country_year":{
        "index_columns":[
                "year_id",
                "country_id",
            ]

    },

    "actor_month":{
        "index_columns":[
            "month_id",
            "actor_id",
        ]
    },

    "actor_year":{
        "index_columns":[
            "year_id",
            "actor_id",
        ]
    },
}
