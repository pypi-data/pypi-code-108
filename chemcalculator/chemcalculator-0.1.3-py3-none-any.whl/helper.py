import re
from collections import Counter

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