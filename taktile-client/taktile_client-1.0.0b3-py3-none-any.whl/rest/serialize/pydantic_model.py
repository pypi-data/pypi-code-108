"""
Pydantic rest serialization
"""


import pydantic


def pydantic_model_serialize(*, value: pydantic.BaseModel) -> str:
    """
    Serialize pandas series

    Parameters
    ----------
    value : pydantic.BaseModel
        value to serialize

    Returns
    -------
    str
        serialized pydantic model
    """
    return value.json()
