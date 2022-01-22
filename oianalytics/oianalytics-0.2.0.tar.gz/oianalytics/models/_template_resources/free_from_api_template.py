from oianalytics import models

from datetime import datetime


def load_data(
    input_parameters: dict,
    current_execution_date: datetime,
    last_execution_date: datetime,
    **kwargs
):
    time_values = models.queries.retrieve_time_values(
        start_date=last_execution_date,
        end_date=current_execution_date,
        aggregation="RAW_VALUES",
    )

    batch_data = models.queries.retrieve_batch_steps_and_data(start_date=last_execution_date,
                                                              end_date=current_execution_date)

    data = {"time_values": time_values, "batch_data": batch_data}

    return data


def load_resource(**kwargs):
    return None


def process_data(data, **kwargs):
    return {"time_values": time_values}
