import re
import pandas as pd
from multiprocessing import Condition
from collections import Counter
from chemcalculator.datasets import get_periodic_table

# read in periodic table and create dictionary
periodic_table = pd.read_csv(get_periodic_table(), skiprows = 2)
periodic_table.set_index('Symbol', drop=True, inplace=True)
periodic_table = periodic_table.to_dict(orient="index")

# gather atomic mass from the periodic table
periodic_table_mass={}
for element in periodic_table:
    periodic_table_mass[element] = periodic_table[element]['AtomicMass']

def compute_mass(chemical):
    """Computes the molar mass of the given chemical compound.

    Parameters
    ----------
    chemical : string
        The molecular formula of the given chemical compound given as a string.

    Returns
    -------
    float
        The molar mass of the given formula in g/mol.

    Raises
    ------
    TypeError
        Entered value is not a string.
    ValueError
        String contains characters that are not allowed.
    ValueError
        String or subcomponent starts with lowercase letter.
    ValueError
        Chemical compound contains element not in periodic table.

    Examples
    --------
    >>> compute_mass("H2O")
    18.01528

    >>> compute_mass("C12H22O11")
    342.3

    >>> compute_mass("Al2(SO4)3")
    342.15
    
    >>> compute_mass("(NH4)HS")
    51.107
    """
    __check_chemical_format(chemical)
    
    raw_elements = __chemical_elements(chemical)
    
    if set(raw_elements.keys()).issubset(periodic_table_mass): pass
    else:
        raise ValueError('Chemical compound contains element not in periodic table.')
    
    # count and sum up all individual elements
    df = pd.DataFrame.from_dict(raw_elements,
                                orient='index',
                                columns = ["Counts"]).reset_index()
    df = df.rename(columns={"index": "Element"})
    
    # map atomic masses from periodic table and multiply by atomic counts
    df['Mass'] = df['Element'].map(periodic_table_mass) * df['Counts']
    
    # sum and return mass
    return df['Mass'].sum()

def moles_grams_converter(formula, mass, convert_to):
    """
    Converts moles to grams or grams to moles

    Parameters
    ----------
    formula : string
        the checmical formula for the conversion
    mass : float
        the mass of molecule that needs to be converted (grams or moles)
    converter : string
        indicates to convert to either "moles" or "grams"

    Returns
    -------
    float
        mass that is converted to either moles or grams

    Examples
    --------
    >>> moles_grams_converter("H2O", 0.05555, "moles")
    1.000

    >>> moles_grams_converter("H2O", 18.01528, "grams")
    1.000
    """
    grams_per_mole = compute_mass(formula)
    if convert_to == "grams":
        result = mass / grams_per_mole
    elif convert_to == "moles":
        result = mass * grams_per_mole
    else:
        raise TypeError("Please enter either 'grams' or 'moles'")

    return round(result, 3)


def percent_mass(compound, element):
    """
    Calculates the percentage mass of an element (or compound) in a compound

    Parameters
    ----------
    compound : string
        the chemical formula of the full compound
    element : string
        the chemical formula of the element or compound of interest

    Returns
    -------
    float
        the percentage mass of the element or compound of interest
    
    Examples
    --------
    >>> percent_mass("H2O", "O")
    88.819
    
    >>> percent_mass("H2O", "H")
    5.59

    >>> percent_mass("H2O", "H2")
    11.181

    >>> percent_mass("NaOH", "OH")
    42.519
    """
    
    __check_chemical_format(compound)
    __check_chemical_format(element)

    perc_mass = 0
    compound_count = __chemical_elements(compound)
    element_count = __chemical_elements(element)

    if set(element_count).issubset(compound_count): 
        for elem in element_count:
            if element_count[elem] <= compound_count[elem]:
                perc_mass = round(compute_mass(element)/compute_mass(compound)*100, 3)
            else:
                raise ValueError("There cannot be more counts of elements in the sub-compound compared to the larger compound")
    else:
        raise ValueError("Please make sure the sub-compound is part of the larger compound")

    print(f"The percentage mass of {element} in {compound} is: {perc_mass} %")
    return perc_mass

def __chemical_elements(chemical):
    """Decomposes a chemical to it's elements.

    Parameters
    ----------
    chemical : string
        The molecular formula of the given chemical compound given as a string.

    Returns
    -------
    dict
        Dictionary of the chemicals elemental components and their counts.
    """
    primary_list = []
    temp_primary_list = []
    compound_list = []
    simplified_compounds_list = []
    raw_element_list = []
    
    def decompose_elements(string):
        """Decompose string into list of components based on capital letters or parenteses."""
        temp_list = re.findall(r'(\(.*?\)\d+)|(\(.*?\))|([A-Z][^A-Z|(]*)', string)
        temp_list = [item for sublist in temp_list for item in sublist]
        temp_list = list(filter(None, temp_list))
        return temp_list
    
    # split major components of the given chemical
    primary_list = decompose_elements(chemical)
    
    # separate compounds from simple elements
    for component in primary_list:
        if re.match('\(.*?\)\d+|\(.*?\)', component):
            compound_list.append(component)
            primary_list.remove(component)
            
    # simplify the compounds
    for compound in compound_list:
        trim = re.findall('\)\d+', compound)
        
        if trim:
            length = len(trim[0])
            units = trim[0][1:]
            simplified_compound = compound[1:]
            simplified_compound = simplified_compound[:-length]
            
        else:
            length = 1
            units = 1
            simplified_compound = compound[1:]
            simplified_compound = simplified_compound[:-length]
        
        for i in range(int(units)):
            simplified_compounds_list.append(simplified_compound)
    
    # decompose compounds
    for compound in simplified_compounds_list:
        temp_list = decompose_elements(compound)
        temp_primary_list = temp_primary_list + temp_list
    
    # merge inital list with decomposed compounds
    primary_list = primary_list + temp_primary_list
    
    # break down multiple atoms (e.g. Al2 = Al + Al)
    for element in primary_list:
        trim = re.findall('\d+', element)
        if trim:
            length = len(trim[0])
            units = trim[0]
            simplified_element = element[:-length]
            
        else:
            length = 0
            units = 1
            simplified_element = element
    
        for i in range(int(units)):
            raw_element_list.append(simplified_element) 
   
    return Counter(raw_element_list)

def __check_chemical_format(chemical):
    """
    Check that the chemical formula has correct format

    Parameters
    ----------
    chemical : string
        chemical formula to check

    Raises
    ------
    TypeError
        Entered value is not a string.
    ValueError
        String contains characters that are not allowed.
    ValueError
        String or subcomponent starts with a lowercase letter.
    """
    allowed_characters = r'[^\(\)A-Za-z0-9]'
    not_allowed_lowercase = r'^[a-z]|\([a-z]'
    if isinstance(chemical, str): pass
    else:
        raise TypeError('Entered value is not a string.')

    if re.search(allowed_characters, chemical):
        raise ValueError('String contains characters that are not allowed.')
    else: pass

    if re.search(not_allowed_lowercase, chemical):
        raise ValueError('String or subcomponent starts with a lowercase letter.')
    else: pass
