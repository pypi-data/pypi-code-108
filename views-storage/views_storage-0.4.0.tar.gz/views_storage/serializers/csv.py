import io
import pandas as pd

from . import serializer


class Csv(serializer.Serializer[pd.DataFrame]):
    def serialize(self, obj: pd.DataFrame) -> bytes:
        return obj.to_csv(index=False).encode()

    def deserialize(self, data: bytes) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(data))
