"""Utility functions module"""


def chunk_it(elements, n_procs):
    """

    Divide elements in chunks according to number of processes.

    :param list elements: list of elements to be divided in chunks
    :param int n_procs: number of available processes

    :return: list of elements to be assigned to every process
    :rtype: list
    """

    avg = len(elements) / n_procs
    out = []
    last = 0.0

    while last < len(elements):
        out.append(elements[int(last):int(last + avg)])
        last += avg
    return out
