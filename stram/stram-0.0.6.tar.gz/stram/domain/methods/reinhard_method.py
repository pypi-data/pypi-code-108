import logging

import numpy as np
import tensorflow as tf
import tensorflow_io as tfio
from decouple import config as env_config

from stram.domain.methods.base_method import BaseMethod
from stram.domain.toolsets.reinhard_toolset import exchange_stats
from stram.domain.toolsets.general_toolset import (
    clip_0_255,
    validate_masks,
    initialize_mask,
)

logger = logging.getLogger(__name__)
tf.config.optimizer.set_jit(env_config('STRAM_TF_JIT', default=False, cast=bool))


class ReinhardMethod(BaseMethod):
    """
    Source: https://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf
    Title: Colour Transfer between Images
    Authors: Erik Reinhard, Michael Ashikhmin, Bruce Gooch, Peter Shirley

    Perform the transfer of colour from one image to another by borrowing statistical
    charactersitics. Both images are converted into LAB space, a colour space where
    the values between different channels are almost completely decorrelated. Then,
    the first and second order stats (mean and std) are computed for both images and
    the stats of the style image are enforced onto the content image by means of
    applying a simple normalization.

    Optionally, one can provide masks that map particular regions from the content
    and style images that will be matched for the colour transfer.
    """

    def __str__(self):
        return 'reinhard'

    def set_up(
        self, config, content_image, style_image, content_mask=None, style_mask=None
    ):
        content_image_reshaped = tf.expand_dims(content_image, axis=0)
        self.content_image_rgb = tf.cast(content_image_reshaped, tf.float32)
        self.content_image_np = content_image

        style_image_reshaped = tf.expand_dims(style_image, axis=0)
        self.style_image_rgb = tf.cast(style_image_reshaped, tf.float32)

        self.content_mask = initialize_mask(content_image, content_mask)
        self.style_mask = initialize_mask(style_image, style_mask)
        validate_masks(self.content_mask, self.style_mask)

        if env_config('STRAM_SUMMARY', default=False, cast=bool):
            self.summarize_initial_tensors(
                content_image_reshaped, style_image_reshaped, content_mask, style_mask
            )

    def process(self, config):
        logger.info('<Reinhard Method>')
        self._step_1_perform_lab_space_stats_application(config.style_strength)

        if env_config('STRAM_SUMMARY', default=False, cast=bool):
            with self.summary_writer.as_default():
                tb_image = tf.cast(self.synthesized_image, tf.uint8)
                tf.summary.image('synthesized', tb_image, step=1)

    def get_synthesized_image(self):
        synthesized_image = np.round(self.synthesized_image.numpy()[0]).astype(np.uint8)
        return np.where(self.content_mask > 0, synthesized_image, self.content_image_np)

    def _step_1_perform_lab_space_stats_application(self, alpha):
        """
        Convert both images to the decorrelated lab space where the mean and std
        are computed. Then normalize the content image using to the stats from
        the style image, while respecting the region mapping given by their
        corresponding masks.

        Args:
            alpha (float): value between 0 and 1 represeting the strength of stylization
        """
        assert 0 <= alpha <= 1.0, 'Styling strength (alpha) must be in range [0..1]'
        content_rgb_input = self.content_image_rgb / 255.0
        style_rgb_input = self.style_image_rgb / 255.0

        content_lab = tfio.experimental.color.rgb_to_lab(content_rgb_input)
        style_lab = tfio.experimental.color.rgb_to_lab(style_rgb_input)

        synthesized_lab = exchange_stats(
            content_lab, style_lab, self.content_mask, self.style_mask
        )
        synthesized_lab = alpha * synthesized_lab + (1 - alpha) * content_lab
        synthesized_rgb = tfio.experimental.color.lab_to_rgb(synthesized_lab)

        self.synthesized_image = clip_0_255(synthesized_rgb * 255.0)
