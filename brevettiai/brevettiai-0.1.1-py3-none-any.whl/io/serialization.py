import json
import numpy as np
import pandas as pd
import brevettiai
from brevettiai.io import IoTools

try:
    from pandas.io.formats.style import Styler
except ImportError:
    class Styler:
        pass


class ObjectJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.number):
            return o.item()
        elif isinstance(o, np.ndarray):
            return {"object": "np.ndarray", "shape": o.shape, "dtype": o.dtype}
        elif isinstance(o, np.dtype):
            return o.name
        elif isinstance(o, pd.DataFrame):
            return {"object": "pd.DataFrame", "shape": o.shape,
                    "dtype": o.dtypes.tolist(), "columns": o.columns.tolist()}
        elif isinstance(o, pd.Series):
            return {"object": "pd.Series", "shape": o.shape, "dtype": o.dtype}
        elif isinstance(o, Styler):
            return o.render()
        elif isinstance(o, IoTools):
            return None
        elif isinstance(o, brevettiai.Module):
            return o.get_config()
        try:
            return {k: v for k, v in o.__dict__.items() if not k.startswith("_")}
        except Exception:
            return str(o)