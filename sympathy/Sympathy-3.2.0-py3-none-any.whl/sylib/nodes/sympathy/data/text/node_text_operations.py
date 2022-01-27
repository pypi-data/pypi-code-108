# This file is part of Sympathy for Data.
# Copyright (c) 2016-2017, Combine Control Systems AB
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
import re
import jinja2

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, deprecated_node
from sympathy.api import exceptions

from sylib.calculator import calculator_model
import sylib.calculator.plugins


class ConcatenateTexts(synode.Node):
    """Concatenate two or more texts with an optional separator."""

    name = 'Concatenate text'
    nodeid = 'org.sysess.sympathy.texts.concatenatetexts'
    author = 'Magnus Sandén'
    version = '1.0'
    icon = 'join_text.svg'
    tags = Tags(Tag.DataProcessing.Text)

    inputs = Ports([
        Port.Custom('text', 'Text part', name='in', n=(2, None, 2))])
    outputs = Ports([Port.Text('Concatenated text', name='out')])

    parameters = synode.parameters()
    parameters.set_string(
        'sep', value='', label='Separator',
        description='A string to be inserted between each part.',
        editor=synode.editors.textedit_editor())

    def execute(self, node_context):
        sep = node_context.parameters['sep'].value
        inputs = node_context.input.group('in')
        text_parts = [p.get() for p in inputs]
        node_context.output['out'].set(sep.join(text_parts))


class ConcatenateTextsList(ConcatenateTexts):
    """Concatenate a list of texts with an optional separator."""
    name = 'Concatenate texts'
    nodeid = 'org.sysess.sympathy.texts.concatenatetextslist'
    inputs = Ports([Port.Texts('Text parts', name='in')])

    def execute(self, node_context):
        sep = node_context.parameters['sep'].value
        text_parts = [p.get() for p in node_context.input['in']]
        node_context.output['out'].set(sep.join(text_parts))


class SplitText(synode.Node):
    """Split a text into multiple parts."""

    name = 'Split text'
    nodeid = 'org.sysess.sympathy.texts.splittext'
    author = 'Magnus Sandén'
    version = '1.0'
    icon = 'split_text.svg'
    tags = Tags(Tag.DataProcessing.Text)

    inputs = Ports([Port.Text('Text', name='in')])
    outputs = Ports([Port.Texts('Text parts', name='out')])

    parameters = synode.parameters()
    parameters.set_string(
        'pattern', value='', label='Pattern',
        description='A pattern which marks where a split should be made.',
        editor=synode.editors.lineedit_editor())
    parameters.set_boolean(
        'use_regex', value=False, label='Use regex',
        desciption='If checked, the pattern is interpreted as a regex. '
                   'Otherwise, the pattern is interpreted as plain text.')

    def execute(self, node_context):
        use_regex = node_context.parameters['use_regex'].value
        pattern = node_context.parameters['pattern'].value
        text = node_context.input[0].get()
        output = node_context.output['out']

        if use_regex:
            text_parts = re.split(pattern, text)
        else:
            text_parts = text.split(pattern)

        for text_part in text_parts:
            item = output.create()
            item.set(text_part)
            output.append(item)


@deprecated_node("4.0.0", "Jinja2 template")
class Jinja2TemplateOld(synode.Node):
    """
    Create and render a jinja2 template. See `Jinja2
    <http://jinja.pocoo.org/>`_ for full syntax of the template engine.

    Use {{column name}} for accessing the first row of a column, or use 'arg'
    inside a jinja for-loop to access full table.

    Example of iterating over each column::

       {% for name in arg.column_names() %}
          The column name is: {{name}}
          The column data is: {% for value in arg.col(name).data %} {{value}} {% endfor %}
       {% endfor %}

    Example of iterating over each row::

       {% for row in arg.to_rows() %}
          {% for value in row %} {{value}} {% endfor %}
       {% endfor %}

    """

    name = 'Jinja2 template (deprecated)'
    nodeid = 'org.sysess.sympathy.texts.jinja2template'
    author = 'Magnus Sandén'
    version = '0.1'
    icon = 'jinja_template.svg'
    description = (
        'Create and render a jinja2 template. Use "{{column name}}" for '
        'access to the first row of columns, or use "arg" inside a jinja '
        'for-loop to access full table.')

    tags = Tags(Tag.Hidden.Replaced)

    parameters = synode.parameters()
    jinja_code_editor = synode.Util.code_editor(language="jinja").value()
    parameters.set_string(
        'template', label="Template", description='Enter template here',
        editor=jinja_code_editor)

    inputs = Ports([Port.Table('Input data', name='in')])
    outputs = Ports([Port.Text('Rendered Template', name='out')])

    def execute(self, node_context):
        infile = node_context.input['in']
        outfile = node_context.output['out']
        parameters = node_context.parameters
        template_string = parameters['template'].value

        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(template_string)

        # Add metadata to template
        metadata = {'arg': infile}
        for col in infile.cols():
            metadata[col.name] = col.data[0].tolist()

        rendered_template = template.render(metadata)
        outfile.set(rendered_template)


class Jinja2Template(synode.Node):
    """
    Create and render a jinja2 template. See `Jinja2
    <http://jinja.pocoo.org/>`_ for full syntax of the template engine.

    Input data can be of any type and is accessed using {{arg}}.

    The examples below assume that the first input is a table.

    Example of iterating over each column::

       {% for name in arg.column_names() %}
          The column name is: {{name}}
          The column data is: {% for value in arg.col(name).data %} {{value}} {% endfor %}
       {% endfor %}

    Example of iterating over one specific column::

       {% for value in arg.col('Foo').data %}
          {{ value }}
       {% endfor %}

    Example of iterating over each row::

       {% for row in arg.to_rows() %}
          {% for value in row %} {{value}} {% endfor %}
       {% endfor %}

    The examples below assume that you have created a tuple or list of tables
    as input::

       {% for tbl in arg %}
          Table name: {{ tbl.name }}
          {% for col in tbl.cols() %}
             {{ col.name }}: {% for x in col.data %} {{x}} {% endfor %}
          {% endfor %}
       {% endfor %}

    Finally, you can connect complex datatypes such as an ADAF to the node::

       {% for name, col in arg.sys['system0']['raster0'].items() %}
          Signal: {{name}}
          Time: {{ col.t }}
          Value:  {{ col.y }}
       {% endfor %}

    Have a look at the :ref:`Data type APIs<datatypeapis>` to see what methods
    and attributes are available on the data type that you are working with.
    """

    name = 'Jinja2 template'
    nodeid = 'org.sysess.sympathy.texts.generic_jinja2template'
    author = 'Magnus Sandén'
    version = '0.1'
    icon = 'jinja_template.svg'
    description = (
        'Create and render a jinja2 template. Use "{{arg}}" for access '
        'to the data.')

    tags = Tags(Tag.DataProcessing.Text)

    parameters = synode.parameters()
    jinja_code_editor = synode.Util.code_editor(language="jinja").value()
    parameters.set_string(
        'template', label="Template", description='Enter template here',
        editor=jinja_code_editor)

    inputs = Ports([Port.Custom('<a>', 'Input', 'in', n=(0, 1, 1))])
    outputs = Ports([Port.Text('Rendered Template', name='out')])

    def execute(self, node_context):
        infile = node_context.input.group('in')
        outfile = node_context.output['out']
        parameters = node_context.parameters
        template_string = parameters['template'].value

        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(template_string)

        env = calculator_model.context
        plugins = sylib.calculator.plugins.available_plugins()
        for plugin in plugins:
            env.update(sylib.calculator.plugins.get_globals_dict(plugin))

        if len(infile) > 0:
            env['arg'] = infile[0]

        try:
            rendered_template = template.render(env)
        except Exception as e:
            raise exceptions.SyDataError(f'Error rendering template, {e}.')
        outfile.set(rendered_template)
