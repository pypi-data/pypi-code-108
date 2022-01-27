# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust

import pandas as pd


class UnpivotTable(synode.Node):
    """
    Unpivot a Table.

    The inverse operation of Pivot Table. The operation transforms data from a 
    wide to a narrow format. The wide form can be considered as a matrix of 
    column values, while the narrow form is a natural encoding of a sparse 
    matrix. When the data types of value columns differ, the varying data is 
    converted to a common data type so the source data can be part of one 
    single column in the new data set.

    """

    name = 'Unpivot Table'
    nodeid = 'org.sysess.sympathy.data.table.unpivottablenode'
    author = 'Emil Staf'
    version = '0.1'
    icon = 'pivot_table.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([Port.Table('Input Table', name='Input')])
    outputs = Ports([Port.Table('Output Table', name='Output')])

    parameters = synode.parameters()
    parameters.set_string('index',
        label='Index column',
        value='',
        description='Column that contains a unique identifier for each row',
        editor=synode.editors.combo_editor(include_empty=True, edit=True))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['index'],
               node_context.input['Input'])

    def execute(self, node_context):
        
        in_table = node_context.input['Input']
        if in_table.is_empty():
            return

        columns = node_context.input['Input'].column_names()

        out_table = node_context.output['Output']
        parameters = node_context.parameters
        
        df = in_table.to_dataframe()

        # order the columns to match order in in_table
        df = df[columns]
        
        # Find index column
        index_col = parameters['index'].value
        if not index_col:
            df['index'] = df.index
            index_col = 'index'

        # value_vars = df.loc[:, df.columns != index_col]
        value_vars = [c for c in columns if c != index_col]

        try:
            # Unpivot happens here
            df_out = pd.melt(df, id_vars=[index_col], value_vars=value_vars)
        except Exception:
            # Ensure either SyDataError or re-raise.
            in_table._require_column(parameters['index'])
            raise

        # rename to match Pivot Table
        df_out = df_out.rename(columns={'variable': 'Column names'})

        # Create new table from DataFrame
        out_table_df = out_table.__class__.from_dataframe(df_out)

        # Write to output table
        out_table.source(out_table_df)

        # set table name using in table
        out_table.set_name(in_table.get_name())


@node_helper.list_node_decorator(['Input'], ['Output'])
class UnpivotTables(UnpivotTable):
    name = 'Unpivot Tables'
    nodeid = 'org.sysess.sympathy.data.table.unpivottablesnode'
