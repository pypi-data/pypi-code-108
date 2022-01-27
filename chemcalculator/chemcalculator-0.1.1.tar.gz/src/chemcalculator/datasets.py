from importlib import resources

def get_periodic_table():
    """Get path to periodic table csv file.

    Returns
    -------
    pathlib.PosixPath
        Path to file.

    """
    with resources.path("chemcalculator.data", "Periodic-Table-of-Elements.csv") as f:
        data_file_path = f
    return data_file_path