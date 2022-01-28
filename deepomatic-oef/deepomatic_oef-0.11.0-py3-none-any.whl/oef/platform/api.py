from .config import form

_models_ = None
_value_to_tag_map_ = None


def load_json():
    """
    Lazy loading of the form.
    """
    global _models_, _value_to_tag_map_

    if _models_ is None:
        form_json = form.json()
        _value_to_tag_map_ = form_json.pop('value_to_tag_map')
        _models_ = form_json['view_types']
        for view_type in _models_:
            _models_[view_type]['value_to_tag_map'] = _value_to_tag_map_

    return _models_, _value_to_tag_map_


def get_default_models(view_type):
    """
    Return the default models for a given view type to forward to the front-end via API

    Args:
        view_type: an instance of ViewType
    """
    models, _ = load_json()
    return models[view_type.value]


def parse_experiment(payload):
    """
    Construct a experiment protobuf from the payload

    Args:
        payload (dict): a dict as sent to the API
    """
    # Pop the model key and create the ExperimentBuilder
    _, value_to_tag_map = load_json()
    return form.parse(payload, value_to_tag_map)
