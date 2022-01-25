
import datetime
import pydantic

class ModelMetadata(pydantic.BaseModel):
    author:        str
    run_id:        int
    queryset_name: str

    train_start:   int
    train_end:     int

    training_date: datetime.datetime
