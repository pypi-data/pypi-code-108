from importlib import resources
import pandas as pd

def get_periodic_table():
    """
    Parse periodic table to output dictionary of masses

    Returns
    -------
    dict
        dictionary containing molecular mass for each element
    """
    with resources.path("chemcalculator.data", "Periodic-Table-of-Elements.csv") as f:
        data_file_path = f
    # read in periodic table and create dictionary
    periodic_table = pd.read_csv(data_file_path, skiprows = 2)
    periodic_table.set_index('Symbol', drop=True, inplace=True)
    periodic_table = periodic_table.to_dict(orient="index")

    # gather atomic mass from the periodic table
    periodic_table_mass={}
    for element in periodic_table:
        periodic_table_mass[element] = periodic_table[element]['AtomicMass']

    return periodic_table_mass