from matplotlib import gridspec
import matplotlib.pylab as plt
import tensorflow as tf
import glob
import imageio
import cv2
import os


def crop_center(image):
    # Returns a cropped square image.
    shape = image.shape
    new_shape = min(shape[1], shape[2])
    offset_y = max(shape[1] - shape[2], 0) // 2
    offset_x = max(shape[2] - shape[1], 0) // 2
    image = tf.image.crop_to_bounding_box(image, offset_y, offset_x, new_shape, new_shape)
    return image


def load_image(image_path, image_size=(256, 256), preserve_aspect_ratio=True):
    # Loads and preprocesses images.
    # Load and convert to float32 numpy array, add batch dimension, and normalize to range [0, 1].
    img = tf.io.decode_image(tf.io.read_file(image_path), channels=3, dtype=tf.float32)[tf.newaxis, ...]
    img = crop_center(img)
    img = tf.image.resize(img, image_size, preserve_aspect_ratio=preserve_aspect_ratio)
    return img


def save_image(img, filename):
    img = tf.bitcast(tf.cast(img[0] * 255, dtype=tf.int8), tf.uint8)
    img = tf.io.encode_jpeg(img)
    filename = tf.constant(f"{filename}")
    tf.io.write_file(filename, img)


def save_to_gif(input_filenames, output_filename, out_size=512):
    with imageio.get_writer(output_filename, mode='I', fps=30) as writer:
        for filename in input_filenames:
            img = imageio.imread(filename)
            img = cv2.resize(img, dsize=(out_size, out_size), interpolation=cv2.INTER_CUBIC)
            writer.append_data(img)
            os.remove(filename)


def show_images(images, titles=('',)):
    n = len(images)
    image_sizes = [image.shape[1] for image in images]
    w = (image_sizes[0] * 6) // 320
    plt.figure(figsize=(w * n, w))
    gs = gridspec.GridSpec(1, n, width_ratios=image_sizes)
    for i in range(n):
        plt.subplot(gs[i])
        plt.imshow(images[i][0], aspect='equal')
        plt.axis('off')
        plt.title(titles[i] if len(titles) > i else '')
    plt.show()
