"""Misc helpers for data manipulation."""
import pickle


def pickle_copy(data: any) -> any:
    """Do deep copy of data using pickle implementation."""
    # Seems to work much faster for small data than copy.deepcopy.
    return pickle.loads(pickle.dumps(data))
