import logging
import json
import functools
import xml.dom.minidom
from itertools import chain, repeat, islice

import numpy as np
import tensorflow as tf
from brevettiai.io import io_tools
from brevettiai.data.image.bayer_demosaic import tf_bayer_demosaic
from brevettiai.data.image import annotation_parser, ImageKeys

log = logging.getLogger(__name__)


def pad_image_to_size(x, target_size, center_padding=False, **kwargs):
    """
    Pad an image to a target size, **kwargs are used to tf.pad
    :param x:
    :param target_size:
    :param kwargs:
    :return:
    """
    diffs = target_size - tf.shape(x)[:2]
    diffs = tf.concat([diffs, [0]], axis=0)
    if center_padding:
        diff0 = diffs // 2
    else:
        diff0 = tf.zeros_like(diffs)

    paddings = tf.transpose([diff0, diffs - diff0])
    return tf.pad(x, paddings, **kwargs)


def resize_image_with_crop_and_pad(x, target_size, resize_method, keep_aspect_ratio, antialias, padding_mode, center_padding=False):
    """
    Resize image with cropping and padding
    :param x:
    :param target_size:
    :param resize_method:
    :param keep_aspect_ratio:
    :param antialias:
    :param padding_mode:
    :param center_padding:
    :return:
    """
    if tf.reduce_all(tf.shape(x) > 0):
        x = tf.image.resize(x, target_size, method=resize_method,
                            preserve_aspect_ratio=keep_aspect_ratio, antialias=antialias)
        return pad_image_to_size(x, target_size, mode=padding_mode, center_padding=center_padding)
    else:
        return tf.zeros(tf.concat([target_size, [tf.shape(x)[2]]], 0))


def rescale(x, scale, offset, dtype=tf.float32):
    """
    Rescale tensor
    :param x:
    :param scale:
    :param offset:
    :param dtype:
    :return:
    """
    return tf.cast(x, dtype) * tf.cast(scale, dtype) + tf.cast(offset, dtype)


def load_file_safe(x, cache_dir=None, io=io_tools):
    """
    Load a file safely
    :param x:
    :param cache_dir:
    :param io:
    :return:
    """
    try:
        assert x
        try:
            x = x.numpy()
        except AttributeError:
            pass
        buf = io.read_file(x, cache_dir)
        return buf or b''
    except Exception as ex:
        #log.error(str(np.array(x), "utf8"), exc_info=ex)
        return b''


def image_view_transform(x, target_size, scale=1, offset=0, **kwargs):
    """
    Transform image such that is has the target size and is scaled accordingly
    :param x: Image tensor
    :param target_size: Target size
    :param scale:
    :param offset:
    :param kwargs: kwargs for resize_image_with_crop_and_pad
    :return:
    """
    if target_size is not None:
        x = resize_image_with_crop_and_pad(x, target_size, **kwargs)

    if scale != 1 or offset != 0:
        x = rescale(x, scale, offset)
    return x


def roi_selection(x, rois=None, crops_joiner=None):
    """
    Create image crops dependent on BOUNDING_BOX specification
    :param x: Image tensor
    :param rois:
    :param crops_joiner: Crops joining function; could be tf.stack, tf.concat, etc.
    :return: list of image crops
    """
    if rois is not None:
        crops = [x[roi[0, 1]:roi[1, 1], roi[0, 0]:roi[1, 0]] for roi in rois]
    else:
        crops = [x]

    if crops_joiner is not None:
        crops = [crops_joiner(crops)]

    return crops


def color_mode_transformation(img, color_mode):
    """Transform images by color_mode"""
    if color_mode is "bayer":
        img = tf.cast(img[None, ..., :1], tf.float32)
        img = tf_bayer_demosaic(img)[0]
    #if color_mode is "rgb":
    #    sh = tf.shape(img)
    #    img = tf.broadcast_dynamic_shape(img, tf.pack([sh[0], sh[1], 3]))
    return img


@functools.lru_cache(maxsize=512)
def load_bcimg_json(path, io=io_tools):
    """Load bcimage json header for sequential data without prefixed frame names"""
    info = json.loads(io.read_file(path))["Image"]
    if info["DType"] == "eGrayScale8":
        channels = 1
    else:
        raise NotImplementedError(f"dtype of bcimg.json '{info['DType']}' not implemented")
    shape = [info["Frames"], info["OriginalSize"]["Height"], info["OriginalSize"]["Width"], channels]

    return f"{{:00d}}.{info['Format']}", np.array(shape, dtype=np.int32)


@functools.lru_cache(maxsize=512)
def load_bcimg_json_prefixed(path, io=io_tools):
    """Load bcimage json header for sequential data with prefixed frame names"""
    info = json.loads(io.read_file(path))["Image"]
    if info["DType"] == "eGrayScale8":
        channels = 1
    else:
        raise NotImplementedError(f"dtype of bcimg.json '{info['DType']}' not implemented")
    shape = [info["Frames"], info["OriginalSize"]["Height"], info["OriginalSize"]["Width"], channels]

    return f"{{:06d}}.{info['Format']}", np.array(shape, dtype=np.int32)


def load_bcimg_frame(path, tile_format, x, io=io_tools):
    """Load bcimage sequence 'tile'"""
    tile_path = io.path.join(tf.strings.regex_replace(path, "(bcimg.json)?$", "").numpy().decode() + "image_files",
                             *tile_format.numpy().decode().format(x.numpy()).split("/"))
    buf = load_file_safe(tile_path, io=io)
    return buf


@functools.lru_cache(maxsize=512)
def load_dzi(path, zoom=-1, io=io_tools):
    buf = io.read_file(path).decode()
    doc = xml.dom.minidom.parseString(buf)

    image = doc.getElementsByTagName("Image")[0]
    size = doc.getElementsByTagName("Size")[0]
    width = int(size.getAttribute("Width"))
    height = int(size.getAttribute("Height"))
    tile_size = int(image.getAttribute("TileSize"))
    tile_overlap = int(image.getAttribute("Overlap"))
    tile_format = image.getAttribute("Format")

    max_dimension = max(width, height)
    max_level = int(np.ceil(np.log2(max_dimension))) + 1
    zoom = zoom % max_level
    tile_format = f"{zoom}/{{}}_{{}}.{tile_format}"
    return tile_format, tile_size, tile_overlap, width, height


@functools.lru_cache(maxsize=256)
def load_dzi_json(path, zoom=-1, io=io_tools):
    buf = io.read_file(path).decode()
    doc = json.loads(buf)

    width = np.int32(doc["Image"]["Size"]["Width"])
    height = np.int32(doc["Image"]["Size"]["Height"])
    tile_size = np.int32(doc["Image"]["TileSize"])
    tile_overlap = np.int32(doc["Image"]["Overlap"])
    tile_format = doc["Image"]["Format"]

    max_dimension = max(width, height)
    max_level = np.int32(np.ceil(np.log2(max_dimension))) + 1

    zoom = zoom % max_level

    tile_format = f"{zoom}/{{}}_{{}}.{tile_format}"
    return tile_format, tile_size, tile_overlap, width, height


def load_dzi_tile(path, tile_format, x, y, io=io_tools):
    tile_path = io.path.join(tf.strings.regex_replace(path, "(image.)?dzi(.json)?$", "").numpy().decode() + "image_files",
                             *tile_format.numpy().decode().format(x.numpy(), y.numpy()).split("/"))
    buf = load_file_safe(tile_path, io=io)
    return buf


def get_tile_func(path, tile_format, tile_size, tile_overlap, channels, io=io_tools):
    """
    Utility to enclose tile getter func in load_image
    :param path:
    :param tile_format:
    :param tile_size:
    :param channels:
    :param io:
    :return:
    """
    def _f(tile_coords):
        x, y = tile_coords

        # Fallback return zeros in desired size
        tile = tf.zeros((tile_size, tile_size, channels), dtype=tf.uint8)

        if x >= 0 and y >= 0:
            buf = tf.py_function(functools.partial(load_dzi_tile, io=io), [path, tile_format, x, y], tf.string,
                                 name="read_image")
            if tf.strings.length(buf) > 0:
                tile = tf.image.decode_image(buf, channels=3 if channels == 3 else 0, expand_animations=False)
                overlap_x = tile_overlap * int(x > 0)
                overlap_y = tile_overlap * int(y > 0)
                tile = pad_image_to_size(tile[overlap_y:tile_size + overlap_y,
                                              overlap_x:tile_size + overlap_x],
                                         target_size=(tile_size, tile_size))

        return tile
    return _f


def load_image(path: str, metadata: dict, channels: int, color_mode: str, io=io_tools):
    """
    Build tf function to load image from a path
    :param channels:
    :param color_mode:
    :param io:
    :return: function returning image after color mode transformations
    """
    if tf.strings.regex_full_match(path, ".*.dzi(.json)?$"):
        zoom_exp_factor = metadata.get(ImageKeys.ZOOM, 1.0)
        scale_exp = tf.math.log(tf.cast(zoom_exp_factor, tf.float32)) / tf.cast(tf.math.log(float(2.0)), tf.float32)
        zoom = -1 - tf.cast(scale_exp, tf.int32)
        # Get metadata
        bbox = tf.cast(tf.clip_by_value(metadata.get(ImageKeys.BOUNDING_BOX, [0, 0, 1, 1]), 0, 2**31-1), tf.int32)

        if tf.strings.regex_full_match(path, ".*.dzi$"):
            tile_format, tile_size, tile_overlap, width, height = tf.numpy_function(functools.partial(load_dzi, io=io),
                                                                 [path, zoom], [tf.string, tf.int32, tf.int32, tf.int32, tf.int32],
                                                                 name="load_dzi_header")
        else: #if tf.strings.regex_full_match(path, ".*.dzi.json$"):
            tile_format, tile_size, tile_overlap, width, height = tf.numpy_function(functools.partial(load_dzi_json, io=io),
                                                                 [path, zoom], [tf.string, tf.int32, tf.int32, tf.int32, tf.int32],
                                                                 name="load_dzi_json_header")
        zoom_exp_factor = tf.cast(zoom_exp_factor, tf.int32)

        # Calculate tiles to collect
        tile_spec = bbox // (tile_size * zoom_exp_factor)
        x_tiles = tf.range(tile_spec[0], tile_spec[2] + 1)
        y_tiles = tf.range(tile_spec[1], tile_spec[3] + 1)

        # **** Replace invalid tiles with "-1" so the do not have to be attempted loaded later on ***
        tile_max_x = int((width - 1) / (zoom_exp_factor * tile_size)) + 1
        tile_max_y = int((height - 1) / (zoom_exp_factor * tile_size)) + 1
        x_tiles_valid = tf.cast(x_tiles < tile_max_x, tf.int32)
        y_tiles_valid = tf.cast(y_tiles < tile_max_y, tf.int32)
        x_tiles = x_tiles * x_tiles_valid - (1 - x_tiles_valid)
        y_tiles = y_tiles * y_tiles_valid - (1 - y_tiles_valid)
        # **** Replace invalid tiles with "-1" so the do not have to be attempted loaded later on ***

        n_tiles_x = tf.cast(len(x_tiles), tf.int32)
        n_tiles_y = tf.cast(len(y_tiles), tf.int32)

        Y, X = tf.meshgrid(y_tiles, x_tiles)

        # Collect tiles
        tiles = tf.map_fn(get_tile_func(path, tile_format, tile_size, tile_overlap, channels, io),
                          [tf.reshape(X, (-1,)), tf.reshape(Y, (-1,))], dtype=tf.uint8)

        # Tile tiles to single image
        tiles = tf.reshape(tiles, (n_tiles_x, n_tiles_y, tile_size, tile_size, channels))
        tiles = tf.transpose(tiles, (1, 2, 0, 3, 4))
        tiles = tf.reshape(tiles, (n_tiles_y * tile_size, n_tiles_x * tile_size, channels))

        # Apply bbox
        view_offset = tile_spec[:2] * tile_size * zoom_exp_factor
        bbox = tf.reshape(tf.reshape(bbox, (2, 2)) - view_offset[None], (-1,)) // zoom_exp_factor

        # Prepare output
        img = tiles[bbox[1]:bbox[3], bbox[0]:bbox[2]]
    else:
        buf = tf.py_function(functools.partial(load_file_safe, io=io), [path], tf.string, name="read_image")
        if tf.strings.length(buf) > 0:
            img = tf.image.decode_image(buf, channels=3 if channels == 3 else 0, expand_animations=False)
            if ImageKeys.BOUNDING_BOX in metadata:
                bbox = metadata[ImageKeys.BOUNDING_BOX]
                img = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]

                # Pad image to target size if bbox is outside image
                sh = tf.shape(img)
                sh_target = (bbox[3] - bbox[1], bbox[2] - bbox[0])
                paddings = ((0, sh_target[0]-sh[0]), (0, sh_target[1]-sh[1]), (0, 0))
                img = tf.pad(img, paddings)
            if ImageKeys.ZOOM in metadata:
                zoom = tf.cast(metadata[ImageKeys.ZOOM], tf.float32)
                size = tf.cast(tf.round(tf.cast(tf.shape(img)[:2], tf.float32) / zoom), tf.int32)
                img = tf.image.resize(img, size=size, preserve_aspect_ratio=True, antialias=True)
                img = tf.cast(tf.round(img), tf.uint8)
        else:
            if ImageKeys.BOUNDING_BOX in metadata:
                bbox = metadata[ImageKeys.BOUNDING_BOX]
                zoom = tf.cast(metadata.get(ImageKeys.ZOOM, 1), tf.float32)
                sh = tf.cast((tf.round(tf.cast(bbox[3] - bbox[1], tf.float32) / zoom),
                              tf.round(tf.cast(bbox[2] - bbox[0], tf.float32) / zoom)), tf.int32)
            elif ImageKeys.SIZE in metadata:
                zoom = tf.cast(metadata.get(ImageKeys.ZOOM, 1), tf.float32)
                sh = tf.cast((tf.round(tf.cast(metadata[ImageKeys.SIZE][1], tf.float32) / zoom),
                              tf.round(tf.cast(metadata[ImageKeys.SIZE][0], tf.float32) / zoom), channels), tf.int32)
            else:
                sh = tf.constant((1, 1), tf.int32)
            img = tf.zeros((sh[0], sh[1], channels), dtype=tf.uint8)

    img = color_mode_transformation(img, color_mode)
    return img


def load_segmentation(path: str, metadata: dict, shape, label_space, io=io_tools):
    """

    :param path:
    :param metadata:
    :param shape: shape of
    :param label_space:
    :param io:
    :return:
    """
    buf = tf.py_function(functools.partial(load_file_safe, io=io),
                         [path], tf.string, name="read_segmentation")

    view = metadata.get(ImageKeys.BOUNDING_BOX, tf.constant(0))
    scale = 1/metadata.get(ImageKeys.ZOOM, 1)
    seg_input = [buf, shape, view, scale]

    def parse_annotation_buffer(buffer, shape, view, scale):
        annotation = json.loads(buffer.decode())
        draw_buffer = np.zeros((shape[2], shape[0], shape[1]), dtype=np.float32)
        view = view if view.shape else None
        segmentation = annotation_parser.draw_contours2_CHW(annotation, label_space, bbox=view,
                                                            scale=scale, draw_buffer=draw_buffer)
        segmentation = segmentation.transpose(1, 2, 0)
        return segmentation.astype(np.float32)

    segmentation = tf.numpy_function(parse_annotation_buffer, seg_input, tf.float32, name="parse_segmentation")
    segmentation = tf.reshape(segmentation, shape)
    return segmentation


def tile2d(x, grid=(10, 10)):
    """
    Function to tile numpy array to plane, eg. images along the first axis
    :param x: numpy array to tile
    :param grid: size of the grid in tiles
    :return: tiled
    """
    generator = chain(x, repeat(np.zeros_like(x[0])))
    return np.vstack([np.hstack(list(islice(generator, int(grid[1])))) for _ in range(int(grid[0]))])


def alpha_blend(x, y, alpha=0.4):
    return alpha * x + (1 - alpha) * y
