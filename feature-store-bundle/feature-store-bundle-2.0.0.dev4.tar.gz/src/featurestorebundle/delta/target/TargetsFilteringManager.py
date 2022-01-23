import re
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
        time_diff: Optional[str] = None,
    ) -> DataFrame:
        df = targets.filter(f.col(get_target_id_column_name()) == target_id)

        if date_from:
            df = df.filter(f.col(get_time_column_name()) >= date_from)

        if date_to:
            df = df.filter(f.col(get_time_column_name()) <= date_to)

        if time_diff:
            df = df.withColumn(get_time_column_name(), self.__shift_time_column(time_diff))

        return df.select(get_id_column_name(), get_time_column_name())

    def __shift_time_column(self, time_diff: str) -> f.col:
        matches = re.match(r"([+-]?[0-9]+)([smhdw])", time_diff)

        if not matches:
            raise Exception("Invalid time format try something like '7d' for seven days")

        periods = {
            "s": "SECONDS",
            "m": "MINUTES",
            "h": "HOURS",
            "d": "DAYS",
            "w": "WEEKS",
        }

        integer_part = matches[1]
        period_part = matches[2]

        return f.col(get_time_column_name()) + f.expr(f"INTERVAL {integer_part} {periods[period_part]}")
