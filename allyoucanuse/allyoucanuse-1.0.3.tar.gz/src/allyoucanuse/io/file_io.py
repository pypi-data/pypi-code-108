from typing import Iterable
import jsonlines

def read_jsonline_file(filename:str)->Iterable:
    """Read a jsonline file

    Parameters
    ----------
    filename : str
        The jsonline file

    Returns
    -------
    Iterable
        [description]

    Example
    -------
    >>> import allyoucanuse as aycu
    >>> content = aycu.read_jsonline_file("tickets.jsonl")
    """
    with jsonlines.open(filename) as f:
        for record in f:
            yield record
