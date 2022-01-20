from typing import Optional
from arthurai.common.constants import Stage, OutputType

def check_has_bias_attrs(model):
    for attr in model.attributes:
        if attr.monitor_for_bias:
            return True 
    return False

def check_attr_is_bias(model, attr_name: str):
    attr = model.get_attribute(attr_name)
    return attr.monitor_for_bias

def get_positive_predicted_class(model):
    """
    Checks if model is a binary classifier. Returns False if multiclass, otherwise returns 
    the name of the positive predicted attribute
    """
    if model.output_type != OutputType.Multiclass:
        return("Not a classifier model.")
    predicted_value_attributes = model.get_attributes(stage=Stage.PredictedValue)
    if len(predicted_value_attributes) != 2:
        return ("Not a binary classifier.")
    for attr in predicted_value_attributes:
        if attr.is_positive_predicted_attribute:
            return attr.name