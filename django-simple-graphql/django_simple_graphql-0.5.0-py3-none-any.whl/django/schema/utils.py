from typing import Type


def get_node_name(model_cls: Type) -> str:
    return f"{model_cls.__name__}"
