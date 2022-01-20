import numpy as np
import pandas as pd

from typing import List as TypeList
from typing import NewType
from typing import Union

from System.Collections.Generic import List as CSList
from System import Array, Double

from .ParameterStructure.Values import SimMultiValueBigTable, SimMultiValueBigTableHeader
from .ParameterStructure.Components import SimComponent
from .ParameterStructure.Components import SimSlot, SimSlotBase, SimChildComponentEntry, ComponentUtils
from .ParameterStructure.Algorithms.Components import ComponentMapping
from .ParameterStructure.Parameters import SimParameter
from .ParameterStructure.Values import SimMultiValueBigTable
from .ParameterStructure.Assets import ContainedResourceFileEntry


SimMultiValueBigTableType = NewType('SimMultiValueBigTable', SimMultiValueBigTable)
ContainedResourceFileEntryType = NewType('ContainedResourceFileEntry', ContainedResourceFileEntry)
SimParameterType = NewType('SimParameter', SimParameter)
SimComponentType = NewType('SimComponent', SimComponent)


def create_component(name=None, **kwargs) -> SimComponent:
    """
    Create a new Simultan component
    :param name: Name of the component; string
    :param kwargs: dictionary; set the components value of the key entry to to key value; Example: {'Visibility': 0, 'IsAutomaticallyGenerated': True}
    :return: ParameterStructure.Components.SimComponent
    """
    new_comp = SimComponent()

    if name is not None:
        new_comp.Name = name

    for key, value in kwargs.items():
        setattr(new_comp, key, value)

    return new_comp


def create_parameter(name='unnamed parameter', value: Union[int, float] = 0, unit:str='None'):
    """
    Creates a new SIMULTAN parameter

    :param name: Parameter name, string
    :param value: Value of the parameter; int or float
    :param unit: Parameter unit, string
    :return:
    """
    return SimParameter(name, unit, value)


def create_resource_reference(component: SimComponentType, resource: ContainedResourceFileEntryType):
    """
    Add a reference to a resource file to a component
    :param component: ParameterStructure.Components.SimComponent
    :param resource: ParameterStructure.Assets.ContainedResourceFileEntry
    :return:
    """
    return ComponentMapping.AddAsset(component, resource, '')


def assign_table_to_param(param: SimParameterType, table: SimMultiValueBigTable):
    """
    Assign a parameters value to a multi_value_pointer
    :param param: ParameterStructure.Components.SimParameter
    :param table: .ParameterStructure.Values.SimMultiValueBigTable
    """
    param.set_MultiValuePointer(table.DefaultPointer)


def add_sub_component(comp: SimComponentType, sub_comp: SimComponentType, slot_name: str, slot_extension: Union[str, int]):
    """
    Add a sub component to a component.

    :param comp: Component to add the subcomponent; ParameterStructure.Components.SimComponent
    :param sub_comp: Component to be added; ParameterStructure.Components.SimComponent
    :param slot_name: Slot name of the sub-component; string
    :param slot_extension: Slot extension of the sub-component; string
    """
    entry = SimChildComponentEntry(SimSlot(SimSlotBase(slot_name), str(slot_extension)),
                                   sub_comp)
    comp.Components.Add(entry)


def create_multi_value_big_table(table_name: str,
                                 column_title: str,
                                 column_headers: TypeList[str],
                                 column_units: TypeList[str],
                                 row_title: str,
                                 row_units: TypeList[str],
                                 row_headers: TypeList[str],
                                 values: np.ndarray) -> SimMultiValueBigTableType:
    """
    Create a multi value big table
    :param table_name: name of the
    :param column_title: column title
    :param column_headers: header of each column
    :param column_units: unit for each column
    :param row_title: row title
    :param row_headers: header of each row
    :param row_units: unit for each row
    :param values: table values
    :return: ParameterStructure.Values.SimMultiValueBigTable
    """

    column_headers_array = Array[SimMultiValueBigTableHeader](
        [SimMultiValueBigTableHeader(str(x[0]), str(x[1])) for x in zip(column_headers, column_units)])
    row_headers_array = Array[SimMultiValueBigTableHeader](
        [SimMultiValueBigTableHeader(str(x[0]), str(x[1])) for x in zip(row_headers, row_units)])

    def make_list(values):
        row = CSList[Double]()
        [row.Add(x) for x in values]
        return row

    rows = np.apply_along_axis(make_list, axis=1, arr=values)
    table_values = CSList[CSList[Double]]()
    [table_values.Add(x) for x in rows]

    table = SimMultiValueBigTable(table_name,
                                  column_title,
                                  row_title,
                                  column_headers_array,
                                  row_headers_array,
                                  table_values)

    return table


def df_to_multi_value_big_table(table_name: str,
                                df: pd.DataFrame,
                                column_title: str = '',
                                column_units: TypeList[str] = None,
                                row_title: str = '',
                                row_units: TypeList[str] = None):
    """
    Create a multi value big table from a pandas Dataframe
    :param df: dataframe
    :param table_name: name of the
    :param column_title: column title
    :param column_units: unit for each column
    :param row_title: row title
    :param row_units: unit for each row
    :return: ParameterStructure.Values.SimMultiValueBigTable
    """
    if column_units is None:
        column_units = [''] * df.columns.shape[0]

    if row_units is None:
        row_units = [''] * df.index.shape[0]

    table = create_multi_value_big_table(table_name=table_name,
                                         column_title=column_title,
                                         row_title=row_title,
                                         column_headers=df.columns,
                                         column_units=column_units,
                                         row_headers=df.index,
                                         row_units=row_units,
                                         values=df.values)

    return table
