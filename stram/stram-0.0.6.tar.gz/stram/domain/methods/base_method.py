from abc import ABC, abstractmethod

import tensorflow as tf
from decouple import config as env_config

from stram.domain.toolsets.general_toolset import (
    colour_mask,
    get_colour_map,
    create_summary_writer,
)


class BaseMethod(ABC):
    @abstractmethod
    def set_up(
        self, config, content_image, style_image, content_mask=None, style_mask=None
    ):
        """
        Set up the method by performing all steps that must be done only for
        initialization.

        Args:
            config (Bunch): configurations for the styling process
            content_image (np.ndarray): the image to apply the style on (uint8)
            style_image (np.ndarray): the image whose style to apply (uint8)
            content_mask (np.ndarray): the mask for the content image (uint8)
            style_mask (np.ndarray): the mask for the style image (uint8)
        """
        pass

    @abstractmethod
    def process(self, config):
        """
        Run the process of applying the style to the content image.

        Args:
            config (Bunch): configurations for the styling process
        """
        pass

    @abstractmethod
    def get_synthesized_image(self):
        """
        Return the synthesized image.

        Returns:
            synthesized_image (np.ndarray): the resulting image (uint8)
        """
        pass

    def summarize_initial_tensors(
        self, content_image_reshaped, style_image_reshaped, content_mask, style_mask
    ):
        """
        Create summary writer and summarize the input images and masks.

        Args:
            content_image_reshaped (tf.Tensor): content image in shape [B, H, W, 3]
            style_image_reshaped (tf.Tensor): style image in shape [B, H, W, 3]
            content_mask (np.array): content mask in shape [H, W, 1] or None
            style_mask (np.array): style mask in shape [H, W, 1] or None
        """
        colour_map = get_colour_map()
        self.summary_writer = create_summary_writer(env_config('STRAM_SUMMARY_PATH'))

        with self.summary_writer.as_default():
            tf.summary.image('content', content_image_reshaped, step=0)
            tf.summary.image('style', style_image_reshaped, step=0)

            if content_mask is not None:
                content_coloured_mask = colour_mask(content_mask, colour_map)
                tf.summary.image('content_mask', content_coloured_mask, step=0)
            if style_mask is not None:
                style_coloured_mask = colour_mask(style_mask, colour_map)
                tf.summary.image('style_mask', style_coloured_mask, step=0)
