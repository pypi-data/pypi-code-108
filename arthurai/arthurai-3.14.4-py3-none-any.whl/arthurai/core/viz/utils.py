import numpy as np
from arthurai.common.constants import OutputType, Stage
from arthurai.common.exceptions import MethodNotApplicableError


def get_pred_and_gt_attrs(arthur_model):
    """Returns the name of the predicted attribute and ground truth attribute for a model.

    :param arthur_model: an ArthurModel object
    """
    if arthur_model.output_type == OutputType.Regression:
        return arthur_model.get_attributes(Stage.PredictedValue)[0].name , arthur_model.get_attributes(Stage.GroundTruth)[0].name
    elif arthur_model.output_type == OutputType.Multiclass:
        return [(attr.name, attr.attribute_link) for attr in arthur_model.get_attributes(Stage.PredictedValue) if attr.is_positive_predicted_attribute][0]
    else:
        raise MethodNotApplicableError()

# coefficients for cubic polyomial with window size of 5
savgol_coefs = np.array([-0.08571429,  0.34285714,  0.48571429,  0.34285714, -0.08571429])

def savgol_filter(signal):
    """ Simple instantiation of Savitzky-Golay filter (cubic).

    :param signal: a numpy 1D array
    """ 
    return np.convolve(signal, savgol_coefs, mode="same")