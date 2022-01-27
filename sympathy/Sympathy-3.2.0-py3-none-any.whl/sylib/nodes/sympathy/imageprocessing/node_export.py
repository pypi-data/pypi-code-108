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
from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

from skimage import io
from sylib.imageprocessing.image import Image
import numpy as np
import os


class SaveImage(node.Node):
    """
    Saves an image to a datasource in the given file format.
    """
    name = 'Save Image'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_save.svg'
    description = 'Saves an image to a datasource in the given file format'
    nodeid = 'syip.saveimage'
    tags = Tags(Tag.ImageProcessing.IO)

    file_formats = ['png', 'gif']
    parameters = node.parameters()
    parameters.set_string(
        'File format', value='png',
        description=('Desired file format of saved file '
                     '(.png or .gif currently available)'),
        editor=node.Util.combo_editor(options=file_formats))

    inputs = Ports([
        Image('Input image', name='image'),
        Port.Datasource(
            'File name before appending file type extension (eg: .png)',
            name='dest')])

    outputs = Ports([
        Port.Datasource(
            'File name after appending file type extension (eg: .png)',
            name='out')])

    def execute(self, node_context):

        image = node_context.input['image'].get_image()
        dest = node_context.input['dest']
        if dest.decode_type() != 'FILE':
            raise NotImplementedError(
                'Image saving must be done to file names.')
        if len(image.shape) > 2 and image.shape[2] not in [1, 3, 4]:
            raise NotImplementedError(
                'Only images with 1, 3, or 4 channels can be exported.')

        if not isinstance(image.dtype, np.uint8):
            image = (image*255.0).astype(np.uint8)
        if len(image.shape) > 2 and image.shape[2] == 1:
            image = image.reshape(image.shape[:2])
        file_format = node_context.parameters['File format'].value

        dest_path = dest.decode_path()
        try:
            # Creating destination path if it does not exist.
            os.makedirs(os.path.dirname(dest_path))
        except Exception:
            pass

        extensions = {'png': '.png', 'gif': '.gif'}
        extension = extensions[file_format]
        if dest_path.endswith(extension):
            full_path = dest_path
        else:
            full_path = dest_path + extension
        node_context.output['out'].encode_path(full_path)
        io.imsave(full_path, image)


class ImageToTable(node.Node):
    """
    Converts an image into a table with a single column.
    """
    name = 'Convert Image to Table'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_to_table.svg'
    description = (
        'Converts an image into a table with a single column per channel or '
        'for the whole image')
    nodeid = 'syip.convert_image_to_table'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()
    parameters.set_string(
        'Column name', value='image', label="Column name",
        description=(
            'Name of column which image data is converted into, '
            'or prefix if multiple columns are generated'))
    parameters.set_boolean(
        'Multiple columns', value=False, label="Multiple columns",
        description='Converts each channel of the image into separate column')
    parameters.set_boolean(
        'Coordinates', value=False, label="Coordinates",
        description=(
            'Adds a column for XY coordinates. Channel coordinate is '
            'also added if multi-columns is false.'))

    inputs = Ports([
        Image('Input image', name='image'),
    ])
    outputs = Ports([
        Port.Table('Table containing image data', name='data'),
        Port.Table('Table containing image meta data', name='meta'),
    ])

    def execute(self, node_context):

        image = node_context.input['image'].get_image()
        column_name = node_context.parameters['Column name'].value
        multi_columns = node_context.parameters['Multiple columns'].value
        gen_coordinates = node_context.parameters['Coordinates'].value

        data_out = node_context.output['data']
        meta_out = node_context.output['meta']
        width = image.shape[1]
        height = image.shape[0]
        channels = 1 if len(image.shape) < 3 else image.shape[2]
        meta_out.set_column_from_array('width', np.array([width]))
        meta_out.set_column_from_array('height', np.array([height]))
        meta_out.set_column_from_array('channels', np.array([channels]))

        if gen_coordinates:
            if multi_columns:
                data_out.set_column_from_array(
                    'X',
                    np.meshgrid(np.arange(width),
                                np.arange(height))[0].flatten())
                data_out.set_column_from_array(
                    'Y',
                    np.meshgrid(np.arange(width),
                                np.arange(height))[1].flatten())
            else:
                data_out.set_column_from_array(
                    'X',
                    np.meshgrid(np.arange(width),
                                np.arange(height),
                                np.arange(channels))[0].flatten())
                data_out.set_column_from_array(
                    'Y',
                    np.meshgrid(np.arange(width),
                                np.arange(height),
                                np.arange(channels))[1].flatten())
                data_out.set_column_from_array(
                    'Ch',
                    np.meshgrid(np.arange(width),
                                np.arange(height),
                                np.arange(channels))[2].flatten())

        if multi_columns:
            for ch in range(channels):
                data_out.set_column_from_array(
                    '{}:{}'.format(column_name, ch),
                    image[:, :, ch].reshape(width * height))
        else:
            data_out.set_column_from_array(
                column_name, image.reshape(width * height * channels))


class ImageToTable2D(node.Node):
    """
    Converts first channel of image into a 2D table with X along columns and
    Y along rows.
    """
    name = 'Convert Image to 2D Table'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_to_table.svg'
    description = (
        'Converts first channel of image into a 2D table with X along columns '
        'and Y along rows.')
    nodeid = 'syip.convert_image_to_table_2d'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()
    inputs = Ports([
        Image('Input image', name='image'),
    ])
    outputs = Ports([
        Port.Table('Table containing image data', name='data'),
    ])

    def execute(self, node_context):
        image = node_context.input['image'].get_image()
        data_out = node_context.output['data']
        height = image.shape[1]
        if len(image.shape) >= 3:
            image = image[:, :, 0]
        for col in range(height):
            data_out.set_column_from_array(
                'Y{}'.format(col), image[:, col])


class TableToImage(node.Node):
    """
    Converts a table into an image using a column each for: data, image width,
    image height and image channels.
    """
    name = 'Convert Table to Image'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_from_table.svg'
    description = ('Converts a table into an image, using columns for data, '
                   'image width, image height and image channels.')
    nodeid = 'syip.convert_table_to_image'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()
    parameters.set_string(
        'Data column', label='Data column name', value='image',
        description='Name of image data column in input table')
    parameters.set_string(
        'Width column', label='Width column name', value='width',
        description='Name of image width column in input table')
    parameters.set_string(
        'Height column', label='Height column name', value='height',
        description='Name of image height column in input table')
    parameters.set_string(
        'Channels column', label='Channels column name',
        value='channels',
        description='Name of image channels column in input table')

    inputs = Ports([
        Port.Table('Table containing image data', name='data'),
        Port.Table('Table containing image meta data', name='meta'),
    ])
    outputs = Ports([
        Image('Input image', name='image'),
    ])

    def execute(self, node_context):
        data = node_context.input['data'].get_column_to_array(
            node_context.parameters['Data column'].value)
        width = node_context.input['meta'].get_column_to_array(
            node_context.parameters['Width column'].value)[0]
        height = node_context.input['meta'].get_column_to_array(
            node_context.parameters['Height column'].value)[0]
        channels = node_context.input['meta'].get_column_to_array(
            node_context.parameters['Channels column'].value)[0]
        im = data.reshape((height, width, channels))
        node_context.output['image'].set_image(im)


class Table2DToImage(node.Node):
    """
    Converts a 2D table into a grayscale image, using columns as X and rows
    as Y positions.
    """
    name = 'Convert 2D Table to Image'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_from_table.svg'
    description = (
        'Converts a 2D table into a grayscale image, using columns as X and '
        'rows as Y positions.')
    nodeid = 'syip.convert_table2d_to_image'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()

    inputs = Ports([
        Port.Table('Table containing image data', name='data'),
    ])
    outputs = Ports([
        Image('Input image', name='image'),
    ])

    def execute(self, node_context):
        tbl = node_context.input['data']
        data = np.array(
            [tbl.get_column_to_array(colname)
             for colname in tbl.column_names()]).T
        node_context.output['image'].set_image(data)
