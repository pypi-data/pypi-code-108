
import datetime
import pydantic

class ModelMetadata(pydantic.BaseModel):
    """
    ModelMetadata
    =============

    Data used to organize model objects.

    parameters:
        author (str): Name of the user that authored the model object.
        run_id (str): Name of the associated run
        queryset_name (str): Name of the queryset used to train the model
        train_start (int): Month identifier for training start date
        train_start (int): Month identifier for training end date
        training_date (datetime.datetime): Timestamp for training date (use datetime.datetime.now())

    """
    author:        str
    run_id:        str
    queryset_name: str

    train_start:   int
    train_end:     int

    training_date: datetime.datetime
