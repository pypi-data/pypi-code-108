from aibro.constant import INPUT_DATA_SIZE_LIMIT_MB
from aibro.tools.utils import get_data_size_mb


def assert_is_tf_model(model):
    assert model.__class__.__module__.startswith(
        "tensorflow"
    ) or model.__class__.__module__.startswith(
        "keras"
    ), "ERROR: model must be a tf/keras model"


def assert_data_type(data, data_name):
    if type(data).__module__ == "numpy":
        size = get_data_size_mb(data)
        assert (
            size <= INPUT_DATA_SIZE_LIMIT_MB
        ), f"{data_name} has size {size} MB exceeding maximum limit of 1G"
    else:
        raise Exception(f"{data_name} must be numpy type")
    return data


def assert_batch_size_type(batch_size):
    assert type(batch_size) == int, "Incorrect type for batch_size (int)"


def assert_epochs_type(epochs):
    assert type(epochs) == int, "Incorrect type for epochs (int)"
