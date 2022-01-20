import datetime
import uuid
from arthurai.common.constants import Stage, OutputType
from arthurai.common.exceptions import ExpectedParameterNotFoundError, MethodNotApplicableError
from arthurai.core.models import ArthurModel
import pandas as pd
from typing import Optional, Any, Tuple, Callable
import pytz



def log_prediction(arthur_model: ArthurModel) -> Callable[[Any], Any]:
    """Decorator to log the inputs and prediction of a model to Arthur. 

    :param arthur_model: A previously-saved ArthurModel object

    Note, the prediction function to be decorated can take optional arguments for logging;
    these should be passed as kwargs into the function to be decorated.
    
    :param inference_timestamp: A timestamp in ISO 8601 format
    :param partner_inference_id: A unique identifier for an inference

    :return: Tuple of (model_prediction, inference_id)
    """
    if arthur_model.output_type not in [OutputType.Regression,  OutputType.Multiclass]:
        raise MethodNotApplicableError("Logging decorator supports only Regression and Multiclass output types.")

    def decorator_send(func):
        def wrapper_send(*args, **kwargs):
            try:
              timestamp = kwargs.pop("inference_timestamp")
            except KeyError:
              timestamp = datetime.datetime.now(pytz.utc)

            try:
              inference_id = kwargs.pop("partner_inference_id")
            except KeyError:
              inference_id = str(uuid.uuid4())

            output = func(*args)

            inference_data = _format_input_data(*args, arthur_model)
            inference_data.update(
                _format_predicted_value_data(output, arthur_model)
            )

            arthur_model.send_inferences([{
                "inference_data": inference_data,
                "partner_inference_id": inference_id,
                "inference_timestamp": timestamp
            }])

            return output, inference_id
        return wrapper_send
    return decorator_send


def _get_attr_ordering(arthur_model):
    """ Return attribute names in order sorted by attr.position
    """
    model_input_attrs = [(attr.name, attr.position) \
                         for attr in arthur_model.get_attributes(Stage.ModelPipelineInput)]
    model_input_attrs.sort(key=lambda t: t[1])
    input_attribute_names = [name for (name, pos) in model_input_attrs]

    predicted_val_attrs = [(attr.name, attr.position) \
                           for attr in arthur_model.get_attributes(Stage.PredictedValue)]
    predicted_val_attrs.sort(key=lambda t: t[1])
    predicted_val_attribute_names = [name for (name, pos) in predicted_val_attrs]
    return input_attribute_names, predicted_val_attribute_names


def _format_input_data(input_vec, arthur_model):
    """ Arrange in ModelPipelineInput data into proper order and construct dict.
    """
    if isinstance(input_vec, pd.DataFrame):
        return input_vec.to_dict(orient="rows")[0]
    else:
        raise MethodNotApplicableError(str(input_vec.__class__) + " not yet supported.")
        input_attribute_names, predicted_val_attribute_names = _get_attr_ordering(arthur_model)
        return dict(zip(input_vec, input_attribute_names))

def _format_predicted_value_data(model_output, arthur_model):
    """ Arrange PredictedValue data into proper order and construct dict.
    """
    try:
        # wrap in an iterable so the model output can be zipped with column names
        # primarily relevant for regression models with a single output
        model_output.__iter__()
    except AttributeError:
        model_output = [model_output]

    _validate_predicted_value_attrs(arthur_model)
    input_attribute_names, predicted_val_attribute_names = _get_attr_ordering(arthur_model)
    return dict(zip(predicted_val_attribute_names, model_output))

def _validate_predicted_value_attrs(arthur_model):
    """Check if the positions of the PredictedValue attributes have been set. If any are None
    then we can't complete the request.
    """
    attr_positions = [attr.position for attr in arthur_model.get_attributes(Stage.PredictedValue)]
    if any([p is None for p in attr_positions]):
        raise ExpectedParameterNotFoundError("Unable to send inference. All PredictedValue attributes must have `position` assigned.")
