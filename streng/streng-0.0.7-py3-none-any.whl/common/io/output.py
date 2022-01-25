'''
Classes for managing output results
'''

import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict
from tabulate import tabulate
from .lists_and_dicts_and_pandas_etc import *


@dataclass
class OutputString:
    """ An output given as a list of strings

        .. uml::

            class OutputString {
            .. members ..
            + data: List[str] = field(default_factory=list)
            }


    Attributes:
        data (List[str]): A list of strings

    """
    data: List[str] = field(default_factory=list)
    # name: str = None

    def __str__(self):
        return '\n'.join(self.data)


@dataclass
class OutputTable:
    """ An output table given as a list of dictionaries.

        .. uml::

            class OutputTable {
            .. members ..
            + data: List[dict] = field(default_factory=list)
            .. properties ..
            + to_markdown()
            + to_panda_dataframe()
            .. methods ..
            + retrieve()
            + retrieve_column_to_list()
            + to_quantity_value()
            }

    It can be converted for presentation (or usage) as a pandas dataframe or a markdown table

    Attributes:
        data (List[dict]): A list of dictionaries

    """
    data: List[dict] = field(default_factory=list)


    @property
    def to_markdown(self):
        """ Converts data (list of dicts) to a markdown table using tabulate.

        Returns:
            str: a markdown table
        """
        return convert_lod_to_md_table(self.data)

    @property
    def to_panda_dataframe(self):
        """ Converts data to a pandas dataframe

        Returns:
            pd.DataFrame: a pandas dataframe
        """
        return convert_lod_to_pddf(self.data)

    def retrieve(self, search_field, search_value, find_field):
        res = [d[find_field] for d in self.data if d[search_field] == search_value]
        return res[0]

    def retrieve_column_to_list(self, column_name):
        return [k[column_name] for k in self.data]

    def to_quantity_value(self, selected_row=0):
        out = OutputTable()
        out.data = convert_dict_to_quantity_value(self.data[selected_row])
        return out

    def __str__(self):
        return self.to_markdown


@dataclass
class OutputExtended:
    """ A class for multiple outputs

        .. uml::

            class OutputExtended {
            .. members ..
            + outputTables: Dict[str, OutputTable] = field(default_factory=dict)
            + outputStrings: Dict[str, OutputString] = field(default_factory=dict)
            .. properties ..
            + print_all_outputStrings()
            .. methods ..
            + save_tofile_all_outputStrings()
            }

    Attributes:
        outputTables (dict[str, OutputTable]): A dictionary of OutputTables with a string key
        outputStrings (dict[str, OutputString]): A dictionary of OutputStrings with a string key

    """
    outputTables: Dict[str, OutputTable] = field(default_factory=dict)
    outputStrings: Dict[str, OutputString] = field(default_factory=dict)

    @property
    def print_all_outputStrings(self):
        all = []

        for key, value in self.outputStrings.items():
            all.extend(value.data)

        return '\n'.join(all)

    def save_tofile_all_outputStrings(self, pathfilename):
        file = open(pathfilename, 'w', encoding='utf8')
        file.write(self.print_all_outputStrings)
        file.close()

