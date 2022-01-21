from typing import Generator


def divide_chunks(l: list, chunk_size: int) -> Generator[list, None, None]:
    """
    Given a list and chunk size, generate n sized slices of list
    
    Parameters
    ----------
    l : list or slicable object
    chunk_size : int, size of each chunk
    
    Yields
    -------
    lists of chunk size slices of given list
    
    """
    for i in range(0, len(l), chunk_size):
        yield l[i:i + chunk_size]