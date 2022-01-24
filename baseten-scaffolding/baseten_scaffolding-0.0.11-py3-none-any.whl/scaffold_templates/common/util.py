import json
import numpy as np


def model_supports_predict_proba(model):
    if not hasattr(model, 'predict_proba'):
        return False
    if hasattr(model, '_check_proba'):  # noqa eg Support Vector Machines *can* predict proba if they made certain choices while training
        try:
            model._check_proba()
            return True
        except AttributeError:
            return False
    return True


class DeepNumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(DeepNumpyEncoder, self).default(obj)
