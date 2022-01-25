
from typing import List, Optional
import datetime
from pydantic import BaseModel, HttpUrl, validator

class RunMetadata(BaseModel):
    """
    RunMetadata
    ===========

    An object which gathers a set of details about a model run:

    properties:

        model_object_id (str):                       A unique identifier that makes it possible to find a binary file containing the model object

        name (str):                                  The name of the run
        author (str):                                The author of the run
        run_date (datetime.datetime):                The date the run was performed

        queryset_name (str):                         The name of the queryset used for the run
        queryset_retrieval_date (datetime.datetime): The date the queryset was retrieved
        training_partition_used (str):               The name of the training partition (from DataPartitioner)
        training_timespan_used (str):                The name of the training timespan (from DataPartitioner)
        columns (List[str]):                         Queryset columns used for training
        dependent_column (str):                      Column used as outcome. Must be in columns.

        code_located_at (HttpUrl):                   Stable URL pointing to the code

    """
    model_object_id:         str

    name:                    str
    author:                  str
    run_date:                datetime.datetime

    queryset_name:           str
    queryset_retrieval_date: datetime.datetime

    training_partition_used: str
    training_timespan_used:  str

    columns:                 List[str]
    dependent_column:        str

    code_located_at:         Optional[HttpUrl]

    @validator("dependent_column")
    def check_dependent_in_columns(self, v, values, **_):
        if "columns" in values and v not in values["columns"]:
            raise ValueError("dependent_column must be one of the columns in the columns field")
        return v

