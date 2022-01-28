import unittest
import os

import tensorflow as tf
from brevettiai.data.image import ImagePipeline, ImageAugmenter
from copy import deepcopy
from brevettiai.data.image.image_augmenter import ImageNoise, ImageFiltering, ImageDeformation, RandomTransformer

def get_resource(path):
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))


class TestImagePipeline(unittest.TestCase):
    def test_image_pipeline_from_config(self):
        ip = ImagePipeline.from_config({"segmentation": {"classes": ["test"]}})

        assert id(ip.segmentation._ip) == id(ip)

    def test_image_pipeline_get_schema(self):
        schema = ImagePipeline.get_schema()


class TestImageAugmentation(unittest.TestCase):
    def test_augmentation_config(self):
        test_img = dict(img=tf.random.uniform((2, 160, 120, 3), dtype=tf.float32))
        init_settings = {
            "random_transformer": {"translate_horizontal": 0.2},
            "image_noise": {"hue": 0.5}
        }

        img_aug = ImageAugmenter.from_settings(deepcopy(init_settings))

        sh = test_img["img"].shape
        img = img_aug(test_img, seed=0)
        assert img["img"].shape == sh

        config = img_aug.get_config()
        for kk, ss in init_settings.items():
            for kk2 in ss:
                assert config[kk][kk2] == ss[kk2]

    def test_image_noise(self):
        test_img = tf.image.decode_bmp(tf.io.read_file(get_resource("bin/0_1543413266626.bmp"), -1))
        test_img = tf.cast(test_img, tf.float32)[None] * [0.5, .1, .9] / 255

        aug_noise_config = {'brightness': 0.25,
                            'contrast': [0.25, 0.5],
                            'hue': 0.5,
                            'saturation': [1.0, 2.0],
                            'stddev': 0.01,
                            'chance': 0.99}
        aug_noise = ImageNoise.from_config(aug_noise_config)
        image_noise = aug_noise(test_img, seed=42)
        assert image_noise is not None
        # TODO: With tensorflow 2.4.0 stateless_uniform and stateless_random_brightness etc
        # Test that image_noise does not change

    def test_image_filtering(self):
        test_img = tf.image.decode_bmp(tf.io.read_file(get_resource("bin/0_1543413266626.bmp"), -1))
        test_img = tf.cast(test_img, tf.float32)[None] * [0.5, .1, .9] / 255
        aug_filter_config = {'emboss_strength': (1.0, 1.25),
                             'avg_blur': (3, 3),
                             'gaussian_blur_sigma': .31,
                             'chance': 0.99}
        aug_filter = ImageFiltering.from_config(aug_filter_config)
        image_filter = aug_filter(test_img, seed=42)
        assert image_filter is not None
        # TODO: With tensorflow 2.4.0 stateless_uniform and stateless_random_brightness etc
        # Test that image_noise does not change

    def test_image_deformation(self):
        test_img = tf.image.decode_bmp(tf.io.read_file(get_resource("bin/0_1543413266626.bmp"), -1))
        test_img = tf.cast(test_img, tf.float32)[None] * [0.5, .1, .9] / 255
        aug_deformation_config = {'alpha': 35.0, 'sigma': 5.0, 'chance': 0.99}
        aug_deformation = ImageDeformation.from_config(aug_deformation_config)
        deformations, probabilities = aug_deformation(tf.shape(test_img), 42)
        image_deformation = aug_deformation.apply(test_img, deformations, probabilities)
        assert image_deformation is not None
        # TODO: With tensorflow 2.4.0 stateless_uniform and stateless_random_brightness etc
        # Test that image_noise does not change

    def test_image_transformation(self):
        test_img = tf.image.decode_bmp(tf.io.read_file(get_resource("bin/0_1543413266626.bmp"), -1))
        test_img = tf.cast(test_img, tf.float32)[None] * [0.5, .7, .9] / 255
        aug_transformer_config = {
            "chance": 0.5,
            "flip_up_down": False,
            "flip_left_right": True,
            "scale": 0.1,
            "rotate": 0,
            "translate_horizontal": 0.1,
            "translate_vertical": 0.1,
            "shear": 0.04,
            "interpolation": "bilinear"
        }
        aug_transformation = RandomTransformer.from_config(aug_transformer_config)
        A = aug_transformation(test_img.shape, 42)
        image_transformation = aug_transformation.transform_images(test_img, A)

        assert image_transformation is not None


if __name__ == '__main__':
    unittest.main()
