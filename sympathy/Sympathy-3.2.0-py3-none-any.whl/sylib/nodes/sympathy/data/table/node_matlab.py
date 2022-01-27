# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
import os

from sylib.matlab import matlab
from sympathy.api import node as synode
from sympathy.api.exceptions import NoDataError
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


common_docs = """
Similar to the function selector, :ref:`F(x)`, one can with this
node apply non-general functions/scripts to the content of Tables.
The difference is that this node uses Matlab as scripting engine
instead of Python. Another difference is that the Python file coming in to
the function selector includes one or many selectable functions, which is
not the case for this node. Here, the Matlab file only consists of a single
written script.

In the Matlab script one reaches the table data in the Table with the arg
variable
::

    in_data = arg

and sets the output in the res variable:
::

    res = out_data

A small example of how to access the input and output data:
::

    names = arg.column_names();
    price = names(1, :);
    price_value = arg.get_column_to_array(price);

    out_table = Table();
    out_table = out_table.set_column_from_array(...
        'MAX_PRICE',  max(price_value), [[], []]);
    out_table = out_table.set_column_from_array(...
        'MIN_PRICE',  min(price_value), [[], []]);
    out_table = out_table.set_table_attributes([]);
    res = out_table;


Some executable examples are located in Sympathy/Matlab/Examples.

See :ref:`Matlab API<matlabapi>` for all functions that can be used on the
input/output table(s).
"""


class SuperNode(synode.Node):
    author = "Sara Gustafzelius"
    version = '1.0'
    description = 'Execute Matlab code'
    icon = 'matlab_fx.svg'
    tags = Tags(Tag.DataProcessing.Calculate)

    def run(self, input_table, output_table, input_script):
        """
        Creates temporary .mat files, writes input data to .mat files,
        runs the matlab script and then reads the output data from .mat file
        and writes it to output.
        """
        script = os.path.abspath(str(input_script.decode_path()))
        in_tmp_file_name = matlab.allocate_mat_file()
        out_tmp_file_name = matlab.allocate_mat_file()

        matlab.write_table_to_matfile(input_table, in_tmp_file_name)
        run_matlab_script(in_tmp_file_name, out_tmp_file_name, script)
        mat_table = matlab.read_matfile_to_table(out_tmp_file_name)
        self.add_output(mat_table, output_table)


class MatlabTables(SuperNode):
    __doc__ = common_docs

    name = 'Matlab Tables'
    nodeid = 'org.sysess.sympathy.data.table.matlabtables'
    inputs = Ports([Port.Datasource('M-file (.m)', name='port2'),
                    Port.Tables('Input Tables', name='port0')])
    outputs = Ports([Port.Tables(
        'Tables with MATLAB script applied', name='port1')])

    def execute(self, node_context):
        input_tables = node_context.input['port0']
        output_tables = node_context.output['port1']
        input_script = node_context.input['port2']
        if input_tables is None:
            raise NoDataError(
                "Can't run calculation when empty input data is connected")

        for input_table in input_tables:
            self.run(input_table, output_tables, input_script)

    def add_output(self, mat_table, output_tables):
        output_tables.append(mat_table)


class MatlabTable(SuperNode):
    __doc__ = common_docs

    author = "Alexander Busck & Sara Gustafzelius"
    name = 'Matlab Table'
    nodeid = 'org.sysess.sympathy.data.table.matlabtable'

    inputs = Ports([Port.Datasource('M-file (.m)', name='port2'),
                    Port.Table('Input Table', name='port0')])
    outputs = Ports([Port.Table(
        'Table with MATLAB script applied', name='port1')])

    def execute(self, node_context):
        input_table = node_context.input['port0']
        output_table = node_context.output['port1']
        input_script = node_context.input['port2']
        if input_table is None:
            raise NoDataError(
                "Can't run calculation when empty input data is connected")

        self.run(input_table, output_table, input_script)

    def add_output(self, mat_table, output_table):
        output_table.update(mat_table)


def run_matlab_script(infile, outfile, script):
    code = (
        "cd('{}');"
        "try "
        "arg = Table();"
        "res = Table();"
        "arg = arg.from_file('{}');"
        "run('{}');"
        "res.to_file('{}');"
        "quit;"
        "catch err "
        "quit;"
        "end;").format(os.path.dirname(script), infile, script, outfile)
    matlab.execute_matlab(code)
