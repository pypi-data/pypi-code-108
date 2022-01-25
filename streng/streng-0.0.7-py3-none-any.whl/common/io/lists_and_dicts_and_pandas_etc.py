"""
module to deal with lists, dictionaries and pandas

| dol: dict of lists
| lod: list of dicts
| pddf: pandas dataframe

    .. uml::

        class lists_and_dicts_and_pandas_etc <<(M,#FF7700)>> {
        .. functions ..
        + convert_lod_to_dol(list_of_dicts)
        + convert_dol_to_lod(dict_of_lists)
        + convert_lod_to_md_table(list_of_dicts)
        + convert_lod_to_pddf(list_of_dicts)
        + convert_dict_to_quantity_value(dict)
        }



"""

from tabulate import tabulate
import pandas as pd


def convert_lod_to_dol(list_of_dicts):
    """
    converts list of dicts --> dict of lists
    """
    _dol = {k: [dic[k] for dic in list_of_dicts] for k in list_of_dicts[0]}
    return _dol


def convert_dol_to_lod(dict_of_lists):
    """
    converts dict of lists --> list of dicts
    """
    _lod = [dict(zip(dict_of_lists, t)) for t in zip(*dict_of_lists.values())]
    return _lod


def convert_lod_to_md_table(list_of_dicts, table_format="pipe", float_fmt=".3E"):
    ftm_tbl = tabulate(list_of_dicts,
                       headers='keys',
                       tablefmt=table_format,
                       floatfmt=float_fmt)
    return ftm_tbl


def convert_lod_to_pddf(list_of_dicts):
    """
        Converts a list of dictionaries to a pandas dataframe

    Args:
        list_of_dicts: a list of dictionaries

    Returns:
        pandas.DataFrame:

    """
    return pd.DataFrame(list_of_dicts,
                       columns=[*list_of_dicts[0]])


def convert_dict_to_quantity_value(dict):
    """
    Args:
        dict (dict): a dictionary

    Returns:
        list: a list of dicts with quantity-value pairs

    """
    return [{'quantity': k, 'value': dict[k]} for k in dict]
