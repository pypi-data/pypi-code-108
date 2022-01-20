#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import os

import mock
from shared.external.models.annotation_transformers.scale import \
    ScaleAnnotation
from shared.tools.misc import json_file_to_dic

my_path = path = os.path.dirname(os.path.abspath(__file__))


def test_get_scaleapi():
    annotation = ScaleAnnotation(json_file_to_dic(
        os.path.join(my_path, 'resources/889fa13h29.ann')))
    assert 'polygon' == annotation.annotation_type
    assert '2019-05-14-17-38-55left_raw_raw_00362.png' == annotation.asset_id
    assert 'Drivable Space' == annotation.annotation_entities[0].label
    assert 15 == len(annotation.annotation_entities[1].coordinates)
    assert 3 == len(annotation.annotation_entities)


def test_get_scaleapi_2():
    annotation = ScaleAnnotation(json_file_to_dic(
        os.path.join(my_path, 'resources/5ecc2f9736e6f30047b66f58.ann')))
    assert 'polygon' == annotation.annotation_type
    assert 'kitti_2011_09_28_drive_2_kitti_camera_color_right_image_raw-1317213980051.png' == annotation.asset_id
    assert 'Bicyclist' == annotation.annotation_entities[0].label
    assert 3 == len(annotation.annotation_entities[0].coordinates)
    assert ["Bicyclist"] == annotation.to_dic().get("labels")


def test_get_scaleapi_3():
    annotation = ScaleAnnotation(json_file_to_dic(
        os.path.join(my_path, 'resources/5eface514847b300269ab604.ann')))
    assert 'polygon' == annotation.annotation_type
    assert 'axis_front_image_raw_compressed_data_1581036613006.jpeg' == annotation.asset_id
    assert 'Sedan' == annotation.annotation_entities[0].label
    assert 3 == len(annotation.annotation_entities[0].coordinates)
    assert 1 == len(annotation.annotation_entities)
    assert "Sedan" in annotation.to_dic().get("labels")
