from pathlib import Path

from .labelme import Labelme
from .labelme import Polygon
from ...utils_vvd import create_uuid
from ...utils_vvd import cv_rgb_imread


def make_ok_labelme(image_path, load_exist=False):
    if Path(image_path).exists():
        json_path = Path(image_path).with_suffix('.json')
        if not json_path.exists() or not load_exist:
            uuid = create_uuid()
            realative_image_path = Path(image_path).name
            image = cv_rgb_imread(image_path)
            H, W = image.shape[:2]

            info = {
                'uuid': uuid,
                'image_path': realative_image_path,
                'height': H, 'width': W,
                'roi': [0, 0, H, W],  # roi in parent_image: xyxy
                'parent_uuid': uuid,
            }
            labelme_info = Labelme(info, [])
        else:
            labelme_info = Labelme.from_json(json_path)
        return labelme_info
    return None


def add_shapes_to_labelme(labelme_obj, shape_list, classname_list, shape_type_list=None):
    assert isinstance(labelme_obj, Labelme), f"labelme_obj {labelme_obj} must be instance of Labelme."
    assert len(shape_list) == len(classname_list), f"boxes number {len(shape_list)} != classname number {len(classname_list)}"
    if shape_type_list is not None:
        assert len(shape_type_list) == len(classname_list), f"shape_type number {len(shape_type_list)} != classname number {len(classname_list)}"
    else:
        shape_type_list = ['polygon'] * len(classname_list)
    for shape, classname, shape_type in zip(shape_list, classname_list, shape_type_list):
        polygon_obj = Polygon(shape, classname, shape_type)
        labelme_obj.shape_list.append(polygon_obj)
