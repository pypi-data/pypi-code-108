from typing import Optional
from datetime import date
from pyspark.sql import DataFrame
from pyspark.sql import functions as f
from featurestorebundle.delta.target.schema import get_target_id_column_name, get_id_column_name, get_time_column_name


class TargetsFilteringManager:
    def get_targets(
        self,
        targets: DataFrame,
        target_id: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> DataFrame:
        df = targets.filter(f.col(get_target_id_column_name()) == target_id)

        if date_from:
            df = df.filter(f.col(get_time_column_name()) >= date_from)

        if date_to:
            df = df.filter(f.col(get_time_column_name()) <= date_to)

        return df.select(get_id_column_name(), get_time_column_name())
