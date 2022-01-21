import typing as t

import numpy as np
import pandas as pd

from iris_hector_patino import __version__ as _version
from iris_hector_patino.config.core import config
from iris_hector_patino.processing.data_manager import load_pipeline

pipeline_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
_price_pipe = load_pipeline(file_name=pipeline_file_name)


def make_prediction(*, input_data: t.Union[pd.DataFrame, np.ndarray]) -> dict:
    """
    Make a prediction using a trained model.
    """
    data = pd.DataFrame(input_data, columns=config.model_config.features_to_combine)
    results = {"predictions": None, "version": _version}
    predictions = _price_pipe.predict(data)
    results.update({"predictions": predictions[0]})
    results.update({"version": _version})
    return results
