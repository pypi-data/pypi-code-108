from pathlib import Path
from ..utils import create_uuid
from ....utils_vvd import cv_rgb_imread
from ....utils_vvd import glob_recursively
from tqdm import tqdm
from .labelme import Labelme


def make_ok_labelme_json(image_path):
    if Path(image_path).exists():
        json_path = Path(image_path).with_suffix('.json')
        if not json_path.exists():
            uuid = create_uuid()
            realative_image_path = Path(image_path).name
            image = cv_rgb_imread(image_path)
            H, W = image.shape[:2]
            imaging = 2

            info = {
                'uuid': uuid,
                'image_path': realative_image_path,
                'height': H, 'width': W,
                'roi': [0, 0, H, W],  # roi in parent_image: xyxy
                'parent_uuid': uuid,
                "imaging": imaging,  # 1,2,3,4
            }

            labelme_info = Labelme(info, [])
            labelme_info.save_json(str(json_path))


def make_ok_labelme_for_dir(root_dir, img_suffix='png'):
    image_path_list = glob_recursively(root_dir, img_suffix)
    for image_path in tqdm(image_path_list):
        make_ok_labelme_json(image_path)