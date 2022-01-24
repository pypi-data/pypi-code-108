import collections

from azureml.core import Environment
from azureml.automl.dnn.vision.common.utils import _pad
from azureml.automl.dnn.vision.common.tiling_dataset_element import TilingDatasetElement
from azureml.automl.dnn.vision.classification.io.read.dataset_wrappers import BaseDatasetWrapper


class RunMock:

    def __init__(self, exp):
        self.experiment = exp
        self.metrics = {}
        self.properties = {}
        self.id = 'mock_run_id'

    def add_properties(self, properties):
        self.properties.update(properties)

    def log(self, metric_name, metric_val):
        self.metrics[metric_name] = metric_val

    def get_environment(self):
        return Environment('test_env')


class ExperimentMock:

    def __init__(self, ws):
        self.workspace = ws


class WorkspaceMock:

    def __init__(self, datastore):
        self._datastore = datastore

    def get_default_datastore(self):
        return self._datastore


class DatastoreMock:

    def __init__(self, name):
        self.name = name
        self.files = []
        self.dataset_file_content = []
        self.workspace = None

    def reset(self):
        self.files = []
        self.dataset_file_content = []

    def path(self, file_path):
        return file_path

    def upload_files(self, files, relative_root=None, target_path=None, overwrite=False):
        self.files.append((files, relative_root, target_path, overwrite))
        if len(files) == 1:
            with open(files[0], "r") as f:
                self.dataset_file_content = f.readlines()


class DatasetMock:

    def __init__(self, id):
        self.id = id


class ObjectDetectionDatasetMock:

    def __init__(self, items, num_classes):
        image_items = []
        tile_items = []
        for item in items:
            if "tile" in item[2]:
                tile_items.append(item)
            else:
                image_items.append(item)

        self._image_urls = [item[2]["filename"] for item in image_items]
        self._image_urls_to_items = {image_url: image_items[idx] for idx, image_url in enumerate(self._image_urls)}

        self._image_tiles = {}
        self._image_tile_to_items = {}
        if tile_items:
            self._supports_tiling = True
            for item in tile_items:
                tile_element = TilingDatasetElement(item[2]["filename"], item[2]["tile"])
                if tile_element.image_url not in self._image_tiles:
                    self._image_tiles[tile_element.image_url] = []
                self._image_tiles[tile_element.image_url].append(tile_element)
                self._image_tile_to_items[tile_element] = item

        self._num_classes = num_classes
        self._classes = ["label_{}".format(i) for i in range(self._num_classes)]
        self._label_to_index_map = {i: self._classes[i] for i in range(self._num_classes)}

    def get_image_url_at_index(self, index):
        return self._image_urls[index]

    def get_image(self, image_url, tile, index):
        if tile is not None:
            return self._image_tile_to_items[TilingDatasetElement(image_url, tile)]
        else:
            return self._image_urls_to_items[image_url]

    def get_image_tiles(self, image_url):
        return self._image_tiles[image_url]

    def supports_tiling(self):
        return self._supports_tiling

    def __len__(self):
        return len(self._image_urls)

    @property
    def num_classes(self):
        return self._num_classes

    def label_to_index_map(self, label):
        return self._label_to_index_map[label]

    def index_to_label(self, index):
        return self._classes[index]

    @property
    def classes(self):
        return self._classes

    def prepare_image_targets_for_eval(self, image_targets, height, width):
        return image_targets


class ClassificationDatasetWrapperMock(BaseDatasetWrapper):
    def __init__(self, items, num_classes):
        self._num_classes = num_classes
        self._priv_labels = ["label_{}".format(i) for i in range(self._num_classes)]
        self._label_freq_dict = collections.defaultdict(int)
        for key in self._priv_labels:
            self._label_freq_dict[key] += 1
        self._items = items
        super().__init__(label_freq_dict=self._label_freq_dict, labels=self._priv_labels)

    def __len__(self):
        return len(self._items)

    def pad(self, padding_factor):
        self._items = _pad(self._items, padding_factor)

    def item_at_index(self, idx):
        return self._items[idx]

    def label_at_index(self, idx):
        return self._priv_labels[idx % self._num_classes]

    @property
    def label_freq_dict(self):
        return self._label_freq_dict
