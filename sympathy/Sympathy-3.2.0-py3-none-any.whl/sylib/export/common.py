# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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

COMMON_DOC = """
The export of data is the final step in an analysis workflow. The analysis
is performed and the result must to be exported to an additional data format
for presentation or visualisation. Or, Sympathy for Data has been used for
data management, where data from different source has been gathered and merged
into a joint structure that can be exported to different data format.

There exists export from the following internal data types:
    - :ref:`Export Tables`
    - :ref:`Export ADAFs`
    - :ref:`Export Texts`
    - :ref:`Export Figures`

The export nodes can also be used for storing partial results on disk.
The stored data can be reimplemented further ahead in the workflow by
connecting the outgoing datasources to an import node.

The export nodes are all based on the use of plugins, the same structure
as the import nodes. Each supported data format has its own plugin, and
may also have a specific GUI settings.
"""
