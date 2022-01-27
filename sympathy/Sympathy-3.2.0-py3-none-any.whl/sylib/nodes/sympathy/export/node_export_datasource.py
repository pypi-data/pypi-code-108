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
from sylib.export import base
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.export import datasource as exportdatasource


class ExportDatasources(base.ExportMultiple, synode.Node):
    """
    This node handles compression/decompression of some common archive formats.

    The following formats are supported:
    * ZIP
    * GZIP
    * TAR

    The ZIP format can compress and store multiple files in a single archive.
    All input files will be put into an archive with the configured name.

    GZIP however only compresses one file at a time. The compressed file will
    have the same name as the original file, but with the added extension .gz.
    Therefore you cannot configure the name.

    To create an archive with multiple files, using GZIP, you have to use two
    nodes in succession. In the first one you will use TAR, which creates one
    file of all the input files, much like the ZIP option, but this file is not
    yet compressed. So in the second node you will use GZIP to compress the TAR
    archive. This results in a file iwth the extension .tar.gz.

    To decompress you then do the same in reverse. First decompress with GZIP
    then extract all files with TAR.
    """

    name = 'Archive files'
    description = 'Compress/decompress files in multiple archive formats.'
    icon = 'export_datasource.svg'
    inputs = Ports([Port.Datasources(
        'Datasources to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    tags = Tags(Tag.Disk.File)
    plugins = (exportdatasource.DatasourceArchiveBase, )
    author = 'Erik der Hagopian'
    nodeid = 'org.sysess.sympathy.export.exportdatasources'
    version = '1.0'

    def update_parameters(self, old_params):
        archive_type = old_params['active_exporter'].value
        if archive_type == 'ZIP':
            old_params['active_exporter'].value = 'ZIP Extractor'
        elif archive_type == 'GZIP':
            old_params['active_exporter'].value = 'GZIP Extractor'

        parameter_dict = old_params._parameter_dict
        custom_data = parameter_dict['custom_exporter_data']

        for old_key, new_key in [('ZIP', 'ZIP Extractor'),
                                 ('GZIP', 'GZIP Extractor')]:
            group = custom_data.pop(old_key, None)
            if group is not None:
                custom_data[new_key] = group
