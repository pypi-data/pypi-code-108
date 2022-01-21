import os
import tensorflow as tf
import tensorflow_hub as hub
from imgFnc import load_image, show_images


def evaluate_hub(content_image_filename, style_image_filename, output_size, style_size, plot_onoff=False):
    # Disable TensorFlow output
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    # Load and preprocess images
    content_image, style_image = load_and_preprocess(content_image_filename, style_image_filename, output_size,
                                                     style_size)
    # Load TF Hub module
    hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
    stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    if plot_onoff:
        show_images([content_image, style_image, stylized_image], ('Content Image', 'Style Image', 'Stylized Image'))

    return stylized_image


def load_and_preprocess(content_image_filename, style_image_filename, output_size, style_size):
    content_image = load_image(content_image_filename, (output_size, output_size))
    style_image = load_image(style_image_filename, (style_size, style_size))
    style_image = tf.nn.avg_pool(style_image, ksize=[3, 3], strides=[1, 1], padding='same')

    return content_image, style_image
