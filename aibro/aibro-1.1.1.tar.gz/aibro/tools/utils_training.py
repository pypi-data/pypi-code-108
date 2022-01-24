from tensorflow.keras.losses import deserialize as loss_deserialize
from tensorflow.keras.metrics import deserialize as metric_deserialize
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import deserialize as optimizer_deserialize

from aibro.tools.utils import unpack_base64_encoded_pickle


def deserialize_model_data(data):
    model: Model = load_model_from_model_content(data.encoded_model_content)
    loss = (
        loss_deserialize(data.loss_config)
        if not isinstance(data.loss_config, str)
        else data.loss_config
    )
    optimizer = (
        optimizer_deserialize(data.optimizer_config)
        if not isinstance(data.optimizer_config, str)
        else data.optimizer_config
    )
    metrics = [
        metric_deserialize(metric_config)
        if not isinstance(metric_config, str)
        else metric_config
        for metric_config in data.metrics_config
    ]
    encoded_train_X = data.encoded_train_X
    encoded_train_Y = data.encoded_train_Y
    encoded_validation_X = data.encoded_validation_X
    encoded_validation_Y = data.encoded_validation_Y

    train_X = unpack_base64_encoded_pickle(encoded_train_X)
    train_Y = unpack_base64_encoded_pickle(encoded_train_Y)
    validation_X, validation_Y = None, None
    if encoded_validation_X is not None:
        validation_X = unpack_base64_encoded_pickle(encoded_validation_X)
        validation_Y = unpack_base64_encoded_pickle(encoded_validation_Y)

    result = {
        "model": model,
        "loss": loss,
        "optimizer": optimizer,
        "metrics": metrics,
        "train_X": train_X,
        "train_Y": train_Y,
        "validation_data": (validation_X, validation_Y),
    }
    return result


def load_model_from_model_content(encoded_model_content):
    model_content = unpack_base64_encoded_pickle(encoded_model_content)
    f = open("saved_model.h5", "wb")
    f.write(model_content)
    f.close()
    model = load_model("saved_model.h5")
    return model
