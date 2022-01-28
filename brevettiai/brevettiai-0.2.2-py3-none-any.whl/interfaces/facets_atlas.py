import math
from brevettiai.data.image.utils import tile2d
from itertools import islice
import numpy as np
import tensorflow as tf
from brevettiai.data.tf_utils import TfEncoder
from tqdm import tqdm

from brevettiai.io import io_tools
import cv2


def create_atlas(dataset, count=None):
    ds = dataset.get_dataset()
    if len(ds.element_spec) > 1:
        ds = ds.map(lambda x, *_: x)
    if len(ds.element_spec.shape) > 3:
        ds = ds.unbatch()
    ds = ds.map(lambda x: tf.cast(x, np.uint8))
    if count:
        ds = ds.take(count)

    images = np.squeeze(np.stack(list(tqdm(ds.as_numpy_iterator(), total=count))))

    atlas_size = int(math.ceil(math.sqrt(len(images))))
    atlas = tile2d(images, (atlas_size, atlas_size))
    return atlas


def build_facets(dataset, facet_dive, facet_sprite=None, count=4096, exclude_rows=None):
    """
    Build facets files
    :param dataset:
    :param facet_dive: path to facets dive json file or facets dive folder path
    :param facet_sprite: path to facets image sprite path
    :param count: max count of items
    :return:
    """
    exclude_rows = exclude_rows if exclude_rows is not None else {"path", "bucket"}
    if facet_sprite is None:
        facet_dir = facet_dive
        facet_dive = io_tools.path.join(facet_dir, "facets.json")
        facet_sprite = io_tools.path.join(facet_dir, "spriteatlas.jpeg")

    samples = islice(dataset.get_samples_numpy(batch=False), count)
    facet_data = [{k: v for k, v in sample.items() if k not in exclude_rows} for sample in samples]
    io_tools.write_file(facet_dive, TfEncoder().encode(facet_data))

    atlas = create_atlas(dataset, count)
    if atlas.ndim == 3 and atlas.shape[2] >= 3:
        atlas = atlas[:, :, :-4:-1] #Convert back to bgr format cv2.cvtColor(, cv2.COLOR_BGR2RGB)
    jpeg_created, buffer = cv2.imencode(".jpeg", atlas)
    assert jpeg_created
    io_tools.write_file(facet_sprite, bytes(buffer))
    return True
