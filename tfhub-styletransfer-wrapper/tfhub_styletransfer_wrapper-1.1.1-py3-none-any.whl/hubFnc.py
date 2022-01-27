import os
import tensorflow as tf
import tensorflow_hub as hub
from tfhub_styletransfer_wrapper.imgFnc import load_image, show_images, save_to_gif, save_image


class StyleHub:
    def __init__(self, cpu_or_gpu='CPU'):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        if cpu_or_gpu == 'cpu' or cpu_or_gpu == 'CPU':
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        elif cpu_or_gpu == 'gpu' or cpu_or_gpu == 'GPU':
            pass
        self.hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
        self.content_image = []
        self.style_image = []

    def load_content(self, content_image_filename, output_size):
        self.content_image = tf.constant(load_image(content_image_filename, (output_size, output_size)))

    def load_style(self, style_image_filename, style_size):
        self.style_image = load_image(style_image_filename, (style_size, style_size))
        self.style_image = tf.constant(tf.nn.avg_pool(self.style_image, ksize=[3, 3], strides=[1, 1], padding='SAME'))

    def evaluate(self, plot_onoff=False):
        stylized_image = self.hub_module(self.content_image, self.style_image)[0]
        if plot_onoff:
            show_images([self.content_image, self.style_image, stylized_image],
                        ('Content Image', 'Style Image', 'Stylized Image'))

        return stylized_image

    def evaluate_recursively(self, n, plot_onoff=False, export_to_gif=False):
        filenames = []
        stylized_image = self.hub_module(self.content_image, self.style_image)[0]
        if export_to_gif:
            filenames.append("test_image/_0.jpg")
            save_image(stylized_image, filenames[0])
        for i in range(n - 1):
            stylized_image = self.hub_module(stylized_image, self.style_image)[0]
            if export_to_gif:
                filenames.append(f"test_image/_{i + 1}.jpg")
                save_image(stylized_image, filenames[i + 1])
        if export_to_gif:
            save_to_gif(filenames, "test_image/out.gif")
        if plot_onoff:
            show_images([self.content_image, self.style_image, stylized_image],
                        ("Content Image", "Style Image", f"Stylized Image after {n} applications"))
