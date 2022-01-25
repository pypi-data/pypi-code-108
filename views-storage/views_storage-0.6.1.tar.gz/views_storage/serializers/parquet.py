import io
import pandas as pd

from . import serializer


class Parquet(serializer.Serializer[pd.DataFrame, bytes]):
    def serialize(self, obj: pd.DataFrame) -> bytes:
        return obj.to_parquet(index=True, engine="pyarrow")

    def deserialize(self, data: bytes) -> pd.DataFrame:
        return pd.read_parquet(io.BytesIO(data))
