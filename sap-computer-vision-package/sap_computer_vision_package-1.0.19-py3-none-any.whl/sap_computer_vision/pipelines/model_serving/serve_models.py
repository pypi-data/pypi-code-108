import os
import pathlib
import warnings
import uuid
import io
import base64
import logging
from collections import namedtuple

import re
import string
import sys
from detectron2.engine.defaults import DefaultPredictor
from detectron2.config import CfgNode
import detectron2.data.detection_utils as utils
from detectron2.data import transforms as T
from sap_computer_vision import setup_loggers
from sap_computer_vision import get_cfg
from sap_computer_vision.modelling.base import adjust_model_configs_base_architecture_to_feature_extraction_node
from sap_computer_vision.data.augs import build_augmentations, generate_aug_cfg_node
from sap_computer_vision.utils.deep_similarity import visualize_similarities
from PIL import Image
import numpy as np

import torch
from slugify import slugify
import jinja2
import click
try:
    import faiss
    got_faiss = True
except ImportError:
    got_faiss = False

logger = logging.getLogger(__name__.split('.')[0])
Index = namedtuple('Index', ['faiss_index', 'file_names', 'labels'])


# TODO: what's up with unused format parameter?
def decode_image(image, format):
    image = Image.open(io.BytesIO(base64.b64decode(image)))
    image = utils._apply_exif_orientation(image)
    return utils.convert_PIL_to_numpy(image, format)


def calculate_similarities(images, predictor, image_format, pooling):
    inputs = []
    for image in images:
        if image_format == "RGB":
            # whether the model expects BGR inputs or RGB
            original_image = original_image[:, :, ::-1]
        height, width = image.shape[:2]
        image = predictor.aug.get_transform(image).apply_image(image)
        image = torch.as_tensor(image.astype("float32").transpose(2, 0, 1))
        inputs.append({"image": image, "height": height, "width": width})
    with torch.no_grad():
        _, pooled, unpooled = predictor.model(inputs, return_pooled_features=True)
    pooled = [p.cpu().numpy() for p in pooled]
    unpooled = [p.cpu().numpy() for p in unpooled]
    result = {}
    idx = range(len(images))
    for i in idx[:-1]:
        for j in idx[i+1:]:
            img_i = images[i]
            img_j = images[j]
            result_i = result.setdefault(i, {})
            result_j = result.setdefault(j, {})
            pooled_i, unpooled_i = [p[i] for p in pooled], [p[i] for p in unpooled]
            pooled_j, unpooled_j = [p[j] for p in pooled], [p[j] for p in unpooled]
            sim_ij, sim_ji = visualize_similarities(img_i,
                                                    unpooled_i,
                                                    pooled_i,
                                                    img_j,
                                                    unpooled_j,
                                                    pooled_j,
                                                    pooling_type=predictor.model.pooling,
                                                    image_format=image_format,)
            result_i[j] = sim_ij.tolist()
            result_j[i] = sim_ji.tolist()
    return result


class Model:
    """
    Serve Models trained with the `sap-computer-vision` package on AIF.
    """
    index_filenames = ['index.npz']
    model_filenames = ['model_best.pth', 'model_final.pth', 'model_*.pth']
    def initialize(self, model_folder):
        setup_loggers(additional_loggers=__name__.split('.')[0])
        model_folder = pathlib.Path(model_folder)
        model_file = self._find_file(model_folder, self.model_filenames)
        cfg = pathlib.Path(model_folder / 'used_config.yaml' )
        if model_folder is None:
            raise RuntimeError(f'No model file found. Model file has to contain at least one file named: {", ".join(self.model_filenames)}')
        with cfg.open() as stream:
            cfg = CfgNode.load_cfg(stream)
        if cfg.MODEL.get('FEATURE_EXTRACTION', None) is None:
            logger.warning('The model config is from an older version of the package. Support for old configs might be'
                'deprecated in future versions. Please use function '
                '\'sap_computer_vision.modelling.base.adjust_model_configs_base_'
                'architecture_to_feature_extraction_node\' to update the config.')
            cfg = adjust_model_configs_base_architecture_to_feature_extraction_node(cfg)
        cfg.MODEL.DEVICE = get_cfg().MODEL.DEVICE
        cfg.MODEL.WEIGHTS = str(model_file)
        try:
            cfg.MODEL.TIMM.PRETRAINED = False
        except (KeyError, AttributeError):
            pass
        self.predictor = DefaultPredictor(cfg)
        aug_cfg = generate_aug_cfg_node(cfg, CfgNode({}), is_train=False)
        self.predictor.aug = build_augmentations(aug_cfg, cfg.INPUT.FORMAT)[0]
        self.task = cfg.TRAINING_INFO.TASK
        self.task = cfg.TRAINING_INFO.TASK
        self.training_info = cfg.TRAINING_INFO
        self.model_cfg = cfg
        self.index = None
        if self.task == 'TRIPLET_DISTANCE_MERIC_LEARNING':
            self.index = self._find_file(model_folder, self.index_filenames)
            if self.index is not None and got_faiss:
                vectors = np.load(self.index)
                vectors, file_names, labels = vectors['vectors'], vectors['file_names'], vectors['labels']
                index = faiss.IndexFlatL2(vectors.shape[1])
                index.add(vectors.astype(np.float32))
                self.index = Index(faiss_index=index, file_names=file_names, labels=labels)


    @staticmethod
    def _find_file(base_dir, candidates):
        if isinstance(candidates, str):
            candidates = [candidates]
        f = None
        for n in candidates:
            l = sorted([*base_dir.glob(n)])
            if len(l) > 0:
                f = l[-1]
                break
        return f

    def predict(self, input_dict):
        results = []
        images = input_dict['images'] if not isinstance(input_dict['images'], str) else [input_dict['images']]
        for img in images:
            res = self.predictor(decode_image(img, self.model_cfg.INPUT.FORMAT))
            if self.task == 'OBJECT_DETECTION':
                res = {**res['instances'].get_fields()}
                res['scores'] = res['scores'].tolist()
                res['pred_boxes'] = res['pred_boxes'].tensor.tolist()
                res['pred_classes'] = res['pred_classes'].tolist()
            elif self.task == 'IMAGE_CLASSIFICATION':
                probs = res.squeeze().cpu().numpy()
                idx_max = np.argmax(probs)
                if self.training_info.get('THING_CLASSES', None) is not None:
                    predicted_class = self.training_info.THING_CLASSES[idx_max]
                else:
                    predicted_class = ''
                res = {'probs': probs.tolist(),
                       'predicted_class_name': str(predicted_class),
                       'predicted_class': int(idx_max)}
            elif self.task == 'TRIPLET_DISTANCE_MERIC_LEARNING':
                embedding = res.squeeze().cpu().numpy()
                res = {'embedding': embedding.tolist()}
            else:
                raise NotImplementedError
            results.append(res)
        return results

    def topk(self, input_dict):
        if self.task != 'TRIPLET_DISTANCE_MERIC_LEARNING':
            raise RuntimeError(f"'topk'-endpoint is only available for 'TRIPLET_DISTANCE_MERIC_LEARNING' models. This is a serving for a '{self.task}' model.")
        if self.index is None:
            raise RuntimeError(f'No index created. [index_file={self.index}; got_faiss={got_faiss}]')
        embeddings = []
        images = input_dict.get('images', [])
        images = input_dict['images'] if not isinstance(images, str) else [input_dict['images']]
        for img in images:
            res = self.predictor(decode_image(img, self.model_cfg.INPUT.FORMAT))
            embeddings.append(res.squeeze().cpu().numpy())
        embeddings = np.array(embeddings, dtype=np.float32)

        top_k = input_dict.get('top_k', 5)
        results = []
        if len(embeddings) > 0:
            distances, indices = self.index.faiss_index.search(embeddings, top_k)
            for dist, idx in zip(distances, indices):
                res = {
                    'distance': dist.tolist(),
                    'catalog_index': idx.tolist(),
                    'catalog_filenames': [str(self.index.file_names[i]) for i in idx],
                    'catalog_labels': [str(self.index.labels[i]) for i in idx]
                }
                results.append(res)
        return results

    def similarity(self, input_dict):
        if self.task not in  ['TRIPLET_DISTANCE_MERIC_LEARNING', 'IMAGE_CLASSIFICATION']:
            raise RuntimeError(f"'similarity_heatmaps'-endpoint is only available for CNN 'TRIPLET_DISTANCE_MERIC_LEARNING' and 'IMAGE_CLASSIFICATION' models. This is a serving for a '{self.task}' model.")
        pooling = self.model_cfg.MODEL.get('FEATURE_EXTRACTION', {}).get('POOL_BACKBONE_FEATURES', False)
        if not pooling:
            raise RuntimeError(f'The feature extraction part of the model does not use a pooling layer. Heatmaps can only be calculated for pooled CNN models.')
        images = input_dict.get('images', [])
        if len(images) < 2:
            raise RuntimeError('Atleast two images are need to calculate similarities.')
        images = input_dict['images'] if not isinstance(images, str) else [input_dict['images']]
        images = [decode_image(img, self.model_cfg.INPUT.FORMAT) for img in images]
        return calculate_similarities(images, self.predictor, self.model_cfg.INPUT.FORMAT, pooling)


TEMPLATE = '''{% for name in labels -%}
{{name}}:
  1:
    py_model_path: {{ paths[loop.index-1] }}
    py_interpreter_path: {{ py_interpreter }}
    py_model_interface_filepath: {{ this_file }}
    py_model_interface_class_name: Model
    __cpu_affinity_friendly__: true
    __do_not_do_cpu_affinity_friendly_eval__: true
{% endfor %}'''
template = jinja2.Template(TEMPLATE)


def retrieve_model_type_and_path(path, separator='//'):
    t, s, p = path.partition(separator)
    if s == separator:
        if len(t) == 0:
            t = None
    else:
        p = t
        t = None
    return t, p


@click.command()
@click.argument('models_string')
@click.option('--check/--no-check', 'check', default=True)
@click.option('--pass-unknown-paths', is_flag=True, default=False)
def create_model_config(models_string: str, check: bool, pass_unknown_paths: bool):
    try:
        MODEL_CONFIG = pathlib.Path(os.environ['MODEL_CONFIG_LIST_FILEPATH_YAML'])
    except KeyError:
        warnings.warning('Environment variable `MODEL_CONFIG_LIST_FILEPATH_YAML` is not set!')

    labels = []
    paths = []
    class_names = []
    for s in models_string.split(':'):
        if len(s) == 0:
            continue
        model_type, s = retrieve_model_type_and_path(s)
        label = re.search(r'\[(.*?)\]',s)
        if label is not None:
            path = s.replace(label.group(), '')
            path = pathlib.Path(path)
            label = slugify(label.group()[1:-1])
            if len(label) == 0:
                label = None
        if label is None:
            path = pathlib.Path(s)
            label = slugify(path.stem)
        label = label.lstrip(string.digits)
        class_name = re.sub("[^0-9a-zA-Z_]+", "", label.replace('-', '_').lstrip(string.digits))
        if check and not path.exists() and not pass_unknown_paths:
            logger.warning(f'Path `{path}` does not exist!')
            break
        elif not path.exists() and pass_unknown_paths:
            txt_file = MODEL_CONFIG.parent / pathlib.Path(f'{uuid.uuid1()}.model_string')
            with txt_file.open('w') as stream:
                stream.write(str(path))
            path = txt_file
        if label not in labels and class_name not in class_names:
            path_str = path if not model_type else f'{model_type}//{path}'
            paths.append(path_str)
            labels.append(label)
            class_names.append(class_name)
    with MODEL_CONFIG.open('w') as stream:
        stream.write(template.render(labels=labels,
                                     paths=paths,
                                     class_names=class_names,
                                     py_interpreter=sys.executable,
                                     this_file=pathlib.Path(__file__).absolute()))


if __name__ == "__main__":
    create_model_config()
