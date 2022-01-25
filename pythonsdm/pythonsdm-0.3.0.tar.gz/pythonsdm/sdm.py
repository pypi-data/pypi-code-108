import json
import pickle

import numpy as np
import scipy.io as sio

from tqdm import tqdm
from pathlib import Path
from numpy import ndarray

from skimage.io import imread, imsave
from skimage.feature import hog
from skimage.draw import disk

from sklearn.linear_model import LinearRegression
from typing import List, Dict, Tuple


def to_array(d: Dict[str, ndarray]) -> ndarray:
    return np.stack([d[k] for k in sorted(d.keys())])


def load_bboxes(bboxes_mat: Path, keys: set) -> ndarray:
    mat = sio.loadmat(bboxes_mat)['bounding_boxes']

    ret = {}
    for bb in mat[0]:
        ret[bb[0][0][0][0].replace('.jpg', '')] = list(bb[0][0][1][0])

    return to_array({
        k: np.asarray(v)
        for k, v in ret.items()
        if k in keys})


def parse_pts(pts: str) -> ndarray:
    pt_list = pts.split('\n')
    pt_list = pt_list[pt_list.index('{') + 1:pt_list.index('}')]
    pt_list = [row.split() for row in pt_list]

    return np.array([
        [round(float(r)), round(float(c))]
        for c, r in pt_list], dtype=np.int32)


def load_pts(path: Path, keys: set) -> ndarray:
    def load(path):
        with open(path) as f:
            return parse_pts(f.read())

    return to_array({
        path.stem: load(path)
        for path in path.glob('*.pts')
        if path.stem in keys})


def load_images(path: Path, limit=None, as_gray=True) -> Tuple[set, List[ndarray]]:
    jpgs = sorted(list(path.glob('*.jpg')))

    if limit:
        jpgs = jpgs[:limit]

    images: List[ndarray] = []
    for jpg in tqdm(jpgs, desc='Loading images'):
        images.append(np.asarray(imread(jpg, as_gray=as_gray)))

    return set([jpg.stem for jpg in jpgs]), images


def shift_scale_shape(shape: ndarray, bbox: ndarray, shape_size=(300, 300)) -> ndarray:
    '''
    shape: (n, 2) markers in the form of [[row, column], ...]
    '''
    assert shape.shape[1] == 2
    x1, y1, x2, y2 = bbox
    w, h = shape_size

    new_shape = np.zeros_like(shape)
    # rows
    new_shape[:, 0] = (shape[:, 0] - y1) * h / (y2 - y1)
    # columns
    new_shape[:, 1] = (shape[:, 1] - x1) * w / (x2 - x1)

    return new_shape


def fit_shape_to_bbox(shape: ndarray, bbox: ndarray, shape_size=(300, 300)):
    assert shape.shape[1] == 2
    x1, y1, x2, y2 = bbox
    w, h = shape_size

    new_shape = np.zeros_like(shape)
    new_shape[:, 0] = shape[:, 0] * (y2 - y1) / h + y1
    new_shape[:, 1] = shape[:, 1] * (x2 - x1) / w + x1

    return new_shape


def calc_avg_shape(
        shapes: ndarray,
        bboxes: ndarray,
        scale_box=(300, 300)) -> ndarray:

    assert len(shapes) == len(bboxes)
    n = len(shapes)

    return np.asarray(sum(
        shift_scale_shape(
            shapes[i],
            bboxes[i],
            scale_box)
        for i in range(n)) / n)


def train_regressor(X: ndarray, y: ndarray):
    assert X.ndim == 2
    assert y.ndim == 2

    regressor = LinearRegression()
    regressor.fit(X, y)

    return regressor


def valid_shapes(images: List[ndarray], shapes: ndarray):
    max_a = np.array([
        np.array(img.shape) - 8
        for img in images])

    return np.maximum(0, np.minimum(shapes, max_a.reshape(-1, 1, 2)))


def get_features(image: ndarray, shape: ndarray):
    shape = shape.astype(np.int32).tolist()

    try:
        return np.concatenate([
            np.asarray(hog(
                image[r:r+8, c:c+8],
                cells_per_block=(1, 1)))

            for r, c in shape])
    except IndexError as e:
        print(image.shape, shape)
        raise e


def get_X(images: List[ndarray], shapes: ndarray):
    assert len(images) == len(shapes)
    return np.stack([
        get_features(images[i], shapes[i])
        for i in range(len(images))])


def get_y(target_shapes: ndarray, shapes: ndarray) -> ndarray:
    assert target_shapes.shape == shapes.shape
    return np.asarray(target_shapes - shapes).reshape(len(target_shapes), -1)


def predict(regressor, X):
    return regressor.predict(X).reshape(len(X), -1, 2)


def mse(actual: ndarray, target: ndarray) -> float:
    return np.mean(np.asarray(actual - target)**2)


def sdm_train(
        train_folder: str,
        bboxes_file: str,
        models: Path = Path('models'),
        num_regressors=5,
        max_samples=2_000):

    models.mkdir(exist_ok=True)

    train_path = Path(train_folder)
    keys, images = load_images(train_path, limit=max_samples)
    bboxes = load_bboxes(Path(bboxes_file), keys)
    target_shapes = load_pts(train_path, keys)

    avg_shape = calc_avg_shape(target_shapes, bboxes)

    with open(models / 'avg_shape.json', 'w') as f:
        json.dump(avg_shape.tolist(), f)

    shapes = valid_shapes(
        images,
        np.asarray([fit_shape_to_bbox(avg_shape, bbox) for bbox in bboxes]))

    bar = tqdm(range(num_regressors))
    for i in bar:
        bar.set_description(f'Training regressors mse {mse(shapes, target_shapes)}')

        X = get_X(images, shapes)
        y = get_y(target_shapes, shapes)

        regressor = train_regressor(X, y)
        with open(models / f'model_{i}.pkl', 'wb') as f:
            pickle.dump(regressor, f)

        shapes = valid_shapes(
            images,
            shapes + predict(regressor, X))


def mark_shapes(images, shapes, color):
    for image, shape in zip(images, shapes):
        for p in shape:
            image[disk(p, 6)] = color


def sdm_test(
        images_folder: str,
        bboxes_file: str,
        models_folder: str = 'models',
        output_folder: str = 'output',
        max_samples=2_000):

    models_path = Path(models_folder)

    regressors = [
        pickle.load(open(model, 'rb'))
        for model in sorted(models_path.glob('*.pkl'))]

    images_path = Path(images_folder)
    keys, images = load_images(images_path, limit=max_samples)
    bboxes = load_bboxes(Path(bboxes_file), keys=keys)

    with open(models_path / 'avg_shape.json') as f:
        avg_shape = np.array(json.load(f))

    shapes = np.stack([
        fit_shape_to_bbox(avg_shape, bbox)
        for bbox in bboxes])

    _, out_images = load_images(images_path, as_gray=False, limit=max_samples)
    mark_shapes(out_images, shapes, [255, 0, 0])

    for i, regressor in tqdm(enumerate(regressors), desc='Predicting'):
        X = get_X(images, shapes)
        shapes = valid_shapes(
            images,
            shapes + predict(regressor, X))

    mark_shapes(out_images, shapes, [0, 255, 0])

    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    for k, img in tqdm(zip(keys, out_images), desc='Saving images'):
        imsave(output_path / f'{k}.jpg', img)
