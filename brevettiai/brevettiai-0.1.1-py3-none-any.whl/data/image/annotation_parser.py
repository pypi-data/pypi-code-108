import json
import logging
import numpy as np
import pandas as pd
from brevettiai.io import io_tools
from brevettiai.data.image import ImageKeys
import uuid

log = logging.getLogger(__name__)

try:
    import cv2
except ImportError as e:
    log.warning("CV2 not available")


def get_points(points, offset=np.array((0, 0)), scale=1):
    """
    Get points from annotation
    Offset is given in original coordinates, and is applied before scaling
    :param points:
    :param offset:
    :param scale:
    :return:
    """
    p = np.fromiter((y for x in points for y in (x["x"], x["y"])),
                    dtype=np.float, count=len(points)*2)
    p.shape = len(points), 2
    p = (p+offset[None])*scale

    return p


def set_points(points):
    pt_list = [None] * len(points)
    for ii, pt in enumerate(points):
        pt_list[ii] = dict(x=pt[0, 0], y=pt[0, 1])
    return pt_list


def get_bbox(annotation):
    """
    Get bounding box bbox from an annotation
    :param annotation:
    :return:
    """
    try:
        if annotation["type"] in {"rectangle", "polygon", "point", "line"}:  # and "roi" in ann["label"]:
            p = get_points(annotation["points"]).astype(np.int)
            return np.concatenate((p.min(axis=0), p.max(axis=0))).clip(min=0), p
    except Exception as ex:
        log.debug("Error getting bounding box bbox of annotation", exc_info=ex)

    return None, None


def sample_points_in_annotation(annotation, tries=100000):
    cnt = make_contour(annotation["points"], annotation["type"])[0]
    if len(cnt) <= 2:
        for i in np.random.choice(np.arange(len(cnt)), size=1000):
            yield cnt[i]
    else:
        _min, _max = cnt.min(axis=0), cnt.max(axis=0)
        _range = (_max - _min)
        for i in range(tries):
            p = (np.random.rand(2) * _range) + _min
            if cv2.pointPolygonTest(cnt, tuple(p), False) >= 0:
                yield np.round(p).astype(np.int)


def get_image_info(annotation_path):
    annotation = json.loads(io_tools.read_file(annotation_path).decode())
    return annotation["image"]


def bounding_box_area(bbox):
    if bbox is not None:
        return (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])
    else:
        return -1


def get_annotations(segmentation_path):
    if len(segmentation_path) > 0:
        ann_file = json.loads(io_tools.read_file(segmentation_path))
        annotations = ann_file.get("annotations", [])
        for a in annotations:
            a[ImageKeys.BOUNDING_BOX], points = get_bbox(a)
            if bounding_box_area(a[ImageKeys.BOUNDING_BOX]) > 0 and a["type"] in {"rectangle", "polygon"}:
                try:
                    a[ImageKeys.INSIDE_POINTS] = np.stack(p for i, p in zip(range(10), sample_points_in_annotation(a)))
                except ValueError:
                    a[ImageKeys.INSIDE_POINTS] = np.stack(points[i % len(points)] for i in range(10))
            elif points is not None:
                a[ImageKeys.INSIDE_POINTS] = np.stack(points[i % len(points)] for i in range(10))
            if "uuid" not in a:
                a["uuid"] = "Missing - " + str(uuid.uuid4())
            for k in ("color", "points"):
                a.pop(k, None)

        return annotations
    else:
        return []


def expand_samples_with_annotations(samples, verbose=1, key="segmentation_path", how="outer"):
    """
    Expand samples DataFrame such that each annotation results in a new sample
    :param samples: Pandas dataframe with
    :param verbose:
    :param key: Key in samples with segmentation path
    :return:
    """
    assert samples.index.is_unique
    if verbose > 0:
        from tqdm import tqdm
        tqdm.pandas()
        apply = samples[key].progress_apply
    else:
        apply = samples[key].apply
    ann = apply(get_annotations)
    ann = ann[ann.str.len() > 0]
    exploded = ann.explode()
    meta = pd.DataFrame(exploded.tolist(), index=exploded.index)
    if "visibility" not in meta.columns:
        meta["visibility"] = -1
    if "severity" not in meta.columns:
        meta["severity"] = -1
    out = pd.merge(samples, meta, left_index=True, right_index=True, how=how)
    out["visibility"].fillna(-1, inplace=True)
    out["severity"].fillna(-1, inplace=True)
    return out


def map_segmentations(annotations, segmentation_mapping):
    for seg in annotations:
        if segmentation_mapping:
            label = segmentation_mapping.get(seg["label"], seg["label"])
            seg["label"] = (label,) if isinstance(label, str) else tuple(label)
        else:
            seg["label"] = (seg["label"],)
    return True


def make_contour(points, anno_type, point_size=1, offset=np.array((0, 0)), scale=1):
    def circle_points(center, r):
        alphas = np.linspace(0, 2 * np.pi, int(np.ceil(2 * np.pi * r)))
        return np.array([center[0] + r * np.cos(alphas), center[1] + r * np.sin(alphas)]).T

    if anno_type == "polygon":
        pt_list = get_points(points, offset, scale)
    elif anno_type == "rectangle":
        pt_list = get_points(points, offset, scale)
        pt_list = np.array([pt_list[[0, 0, 1, 1], 0], pt_list[[0, 1, 1, 0], 1]]).T
    elif anno_type == "point":
        pt_list = get_points(points, offset, scale).astype(np.int)
        if point_size > 1:
            r = int(np.ceil(point_size / 2.0))
            pt_list = circle_points(pt_list[0, 0], r)
    elif anno_type == "line":
        pt_list = get_points(points, offset, scale)
        pt_list = np.floor(pt_list).astype(np.int)
        return [pt_list[ii:ii+2] for ii in range(len(pt_list)-1)]
    else:
        return None

    # drawContours works with pixel centers, but annotation tool use upper left corner as reference
    return [np.floor(pt_list).astype(np.int)]


def draw_contours2(segmentation, label_space, bbox=None, draw_buffer=None, drawContoursArgs=None, **kwargs):
    """
    If more than four channels are in the label space only values 1 will be drawn to the segmentation
    :param segmentation:
    :param label_space:
    :param bbox: bbox of annotation to generate [x0,y0,x1,y1]
    :param draw_buffer: input draw buffer, use to draw on top of existing images
    :param drawContoursArgs: Args for drawContours.. eg thickness to draw non filled contours
    :param kwargs: args for make_contours
    :return:
    """
    if drawContoursArgs is None:
        drawContoursArgs = dict(thickness=cv2.FILLED)

    if draw_buffer is None:
        # Apply bbox to shape for buffer
        if bbox is None:
            shape = (segmentation["image"]["height"], segmentation["image"]["width"])
        else:
            shape = (bbox[3] - bbox[1], bbox[2] - bbox[0])
        first_label = next(iter(label_space.values()))
        shape = (*shape, len(first_label))
        cont = np.zeros(shape, dtype=np.float32)
    else:
        cont = draw_buffer

    if bbox is not None:
        kwargs["offset"] = -bbox[:2]

    for lbl, color in label_space.items():
        color = color if isinstance(color, (tuple, list)) else color.tolist()
        contours = []
        for anno in segmentation["annotations"]:
            if lbl == anno["label"] or (isinstance(lbl, tuple) and np.any([lbl_ii == anno["label"] for lbl_ii in lbl])):
                contour = make_contour(anno["points"], anno["type"], **kwargs)
                if contour is not None:
                    contours.extend(contour)

        # If any contours are found, draw non zero label items
        if len(contours):
            for i, c in enumerate(color):
                if c != 0:
                    cont[..., i] = cv2.drawContours(cont[..., i].copy(), contours, -1, c, **drawContoursArgs)

    return cont


def draw_contours2_CHW(segmentation, label_space, bbox=None, draw_buffer=None, drawContoursArgs=None, **kwargs):
    """
    If more than four channels are in the label space only values 1 will be drawn to the segmentation
    :param segmentation:
    :param label_space:
    :param bbox: bbox of annotation to generate [x0,y0,x1,y1]
    :param draw_buffer: input draw buffer, use to draw on top of existing images
    :param drawContoursArgs: Args for drawContours.. eg thickness to draw non filled contours
    :param kwargs: args for make_contours
    :return:
    """
    if drawContoursArgs is None:
        drawContoursArgs = dict(thickness=cv2.FILLED)

    if draw_buffer is None:
        # Apply bbox to shape for buffer
        if bbox is None:
            shape = (segmentation["image"]["height"], segmentation["image"]["width"])
        else:
            shape = (bbox[3] - bbox[1], bbox[2] - bbox[0])
        first_label = next(iter(label_space.values()))
        shape = (len(first_label), *shape)
        cont = np.zeros(shape, dtype=np.float32)
    else:
        cont = draw_buffer

    if bbox is not None:
        kwargs["offset"] = -bbox[:2]

    for lbl, color in label_space.items():
        contours = []
        for anno in segmentation["annotations"]:
            if lbl == anno["label"] or (isinstance(lbl, tuple) and np.any([lbl_ii == anno["label"] for lbl_ii in lbl])):
                contour = make_contour(anno["points"], anno["type"], **kwargs)
                if contour is not None:
                    contours.extend(contour)

        # If any contours are found, draw non zero label items
        if len(contours):
            color = color if isinstance(color, (tuple, list)) else color.tolist()
            for i, c in enumerate(color):
                if c != 0:
                    cv2.drawContours(cont[i], contours, -1, c, **drawContoursArgs)
    return cont
