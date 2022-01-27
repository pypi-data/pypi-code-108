import re
import cv2
import sys
import cv2 as cv
from mtutils.utils_vvd.box_processing import get_xyxy
import numpy as np
import PIL.Image as Image

import matplotlib
import matplotlib.pyplot as plt
import math

from .utils import is_number, vvd_round
from .utils import is_path_obj
from .utils import current_system
from .utils import is_integer
from .utils import OS_exists
from .utils import time_reduce
from .utils import glob_recursively
from .utils import has_chinese_char

from tqdm import tqdm
from pathlib import Path
from pathlib2 import Path as Path2

from numpy.lib.function_base import iterable
from matplotlib.backends.backend_agg import FigureCanvasAgg
from .array_processing import get_Several_MinMax_Array


popular_image_suffixes = ['png', 'jpg', 'jpeg', 'bmp']

def show_hist(img):
    rows, cols = img.shape
    hist = img.reshape(rows * cols)
    histogram, bins, patch = plt.hist(hist, 256, facecolor="green", histtype="bar")  # histogram即为统计出的灰度值分布
    plt.xlabel("gray level")
    plt.ylabel("number of pixels")
    plt.axis([0, 255, 0, np.max(histogram)])
    plt.show()
    return histogram


def image_resize(img_source, shape=None, factor=None, unique_check=False, interpolation=None):
    image_H, image_W = img_source.shape[:2]
    if shape is not None:
        if is_number(shape):
            shape = [shape] * 2
        shape = vvd_round(shape)

        resized_image = cv2.resize(img_source, shape)

    elif factor is not None:
        if iterable(factor):
            assert len(factor) == 2
            factor_x, factor_y = factor
        else:
            factor_x, factor_y = factor, factor

        resized_H = int(round(image_H * factor_y))
        resized_W = int(round(image_W * factor_x))

        resized_image = cv2.resize(img_source, [resized_W, resized_H], interpolation=interpolation)

    elif shape is None and factor is None:
        resized_image = img_source
    else:
        raise RuntimeError

    if unique_check:
        pixel_list = np.unique(img_source).tolist()
        if len(pixel_list) == 2 and 0 in pixel_list:
            resized_image[resized_image > 0] = np.max(pixel_list)

    return resized_image


def to_gray_image(img):
    if isinstance(img, Path) or isinstance(img, Path2):
        if img.exists():
            gray_img = cv_rgb_imread(img, gray=True)
            return gray_img
        else:
            raise FileNotFoundError(f"file not found {str(img)}")
    elif isinstance(img, str):
        if OS_exists(img):
            gray_img = cv_rgb_imread(img, gray=True)
            return gray_img
        else:
            raise FileNotFoundError(f"file not found {str(img)}")
    elif isinstance(img, np.ndarray):
        if img.ndim == 2:
            return img.copy()
        elif img.ndim == 3:
            return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            raise RuntimeError(f"ndim of img is not 2 or 3 {img.shape}")
    else:
        raise RuntimeError(f"unknown data type {type(img)}")


def median_transfer(image, gray=False, target_median=120):
    if gray:
        image = to_gray_image(image)
    median = max(1, np.median(image))
    mapped_image = (np.clip(image * (target_median / median), 0, 255)).astype('uint8')
    return mapped_image


def to_colorful_image(image):
    """
    make a gray image to an image with 3 channels
    """
    if image.ndim == 2:
        if str(image.dtype) == 'bool':
            image = image.astype('uint8') * 255
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return image


def img_normalize(img, mean, std, to_rgb=False):
    """Inplace normalize an image with mean and std.

    Args:
        img (ndarray): Image to be normalized.
        mean (ndarray): The mean to be used for normalize.
        std (ndarray): The std to be used for normalize.
        to_rgb (bool): Whether to convert to rgb.

    Returns:
        ndarray: The normalized image.
    """
    # cv2 inplace normalization does not accept uint8
    img = img.astype('float32')

    mean = np.array(mean, dtype='float32')
    std = np.array(std, dtype='float32')

    mean = np.float64(mean.reshape(1, -1))
    stdinv = 1 / np.float64(std.reshape(1, -1))
    if to_rgb:
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)  # inplace
    cv2.subtract(img, mean, img)  # inplace
    cv2.multiply(img, stdinv, img)  # inplace
    return img


def gamma_transform(image, theta):
    # gamma transform
    data = np.arange(256)
    data = data / 255
    data = data ** theta
    data = (data * 255).astype('uint8')
    
    gamma_image = data[image]
    return gamma_image


def img_rotate(img,
             angle,
             center=None,
             interpolation=cv2.INTER_LINEAR,
             border_mode=cv2.BORDER_CONSTANT,
             border_value=0,
             auto_bound=False,
             ):
    """Rotate an image.

    Args:
        img (ndarray): Image to be rotated.
        angle (float): Rotation angle in degrees, positive values mean
            clockwise rotation.
        center (tuple[float], optional): Center point (w, h) of the rotation in
            the source image. If not specified, the center of the image will be
            used.
        border_value (int): Border value.
        auto_bound (bool): Whether to adjust the image size to cover the whole
            rotated image.

    Returns:
        ndarray: The rotated image.
    """
    type = img.dtype
    img = img.astype('uint8')
    scale=1.0
    if center is not None and auto_bound:
        raise ValueError('`auto_bound` conflicts with `center`')
    h, w = img.shape[:2]
    if center is None:
        center = ((w - 1) * 0.5, (h - 1) * 0.5)
    assert isinstance(center, tuple)

    matrix = cv2.getRotationMatrix2D(center, -angle, scale)
    if auto_bound:
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_w = h * sin + w * cos
        new_h = h * cos + w * sin
        matrix[0, 2] += (new_w - w) * 0.5
        matrix[1, 2] += (new_h - h) * 0.5
        w = int(np.round(new_w))
        h = int(np.round(new_h))
    rotated = cv2.warpAffine(
        img,
        matrix, (w, h),
        flags=interpolation,
        borderValue=border_value,
        borderMode=border_mode)
    rotated.astype(type)
    return rotated


def cv_rgb_imread(image_path, gray=False):
    """
    按照RGB顺序使用cv读取图像
    """
    image_path = str(image_path)
    image = image_read(image_path)
    if gray:
        if image.ndim > 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        b, g, r = cv.split(image)
        image = cv.merge([r, g, b])

    return image


def cv_rgb_bgr_convert(image):
    """[convert rgb to bgr or bgr ro rgb]

    Args:
        image ([np.array(uint8)]): [uint8 image]

    Returns:
        [image]: [r and b swapped]
    """
    b, g, r = cv.split(image)
    image = cv.merge([r, g, b])

    return image


def image_show(image, window_name='image show'):
    '''
    更加鲁棒地显示图像包括二维图像,第三维度为1的图像
    '''
    temp_image = extend_image_channel(image)
    cv_image_show(image=temp_image, window_name=window_name)


def image_read(image_path, channel=3):
    """
    读取图像，可包含中文路径
    Args:
        image_path ([str]): [图像路径]
        channel (int, optional): [图像通道数，-1为默认，0为灰度]. Defaults to -1.
    """
    image_path = str(image_path)
    return cv.imdecode(np.fromfile(image_path, dtype=np.uint8), channel)


def cv_image_show(image, window_name='image show'):
    '''
    show image (for debug)
    press anykey to destory the window 

    image: image in numpy 
    window_name: name of the window

    image color - bgr
    '''
    cv.namedWindow(window_name, cv.WINDOW_NORMAL)
    cv.imshow(window_name, image)
    cv.waitKey(0)
    cv.destroyAllWindows()


def extend_image_channel(input_image):
    '''
    cv显示三通道图像，本函数将原始图像扩展到三通道
    '''
    image = input_image.copy()

    shape = image.shape

    max_value = np.max(image)
    if not is_integer(max_value) and max_value > 1:
        image /= np.max(image)

    if 0 < np.max(image) <= 1:
        image = (255*image).astype('uint8')


    if len(shape) == 3:
        if shape[2] == 3:
            return image
        elif shape[2] == 1:
            temp_image = np.zeros([shape[0], shape[1], 3])
            for i in range(3):
                temp_image[:, :, i] = image[:, :, 0]
            return temp_image
        else:
            raise TypeError('image type error')
    elif len(shape) == 2:
        temp_image = np.zeros([shape[0], shape[1], 3], dtype=type(image[0][0]))
        for i in range(3):
            temp_image[:, :, i] = image
        return temp_image
    else:
        raise TypeError('image type error')

def cv_bgr_imwrite(bgr_image, image_save_path, para=None, with_suffix=None, factor=1):
    rgb_image = cv_rgb_bgr_convert(bgr_image)
    cv_rgb_imwrite(rgb_image, image_save_path, para, with_suffix, factor)

def cv_rgb_imwrite(rgb_image, image_save_path, para=None, with_suffix=None, factor=1):
    """
    [cv2 save a rgb image]
    Args:
        rgb_image ([np.array]): [rgb image]
        image_save_path ([str/Path]): [image save path]
    """
    image = rgb_image
    if rgb_image.ndim == 3:
        if rgb_image.shape[2] == 3:
            bgr_image = cv_rgb_bgr_convert(rgb_image)
            image = bgr_image

    image_save_path = Path(image_save_path)
    image_save_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = image_save_path.suffix.lower()
    quality_para = None
    if para is not None:
        if suffix == '.jpg' or suffix == '.jpeg':
            # para in 0-100, the bigger the image quality higher and the file size larger
            quality_para = [cv2.IMWRITE_JPEG_QUALITY, para]
        elif suffix == '.png':
            # para in 0-9, the bigger the image file size smaller
            quality_para = [cv2.IMWRITE_PNG_COMPRESSION, para]
    if with_suffix is not None:
        image_save_path = Path(image_save_path).with_suffix('.' + with_suffix)
    
    if factor != 1:
        image = image_resize(image, factor=factor)

    save_path = str(image_save_path)
    if has_chinese_char(save_path):
        cv2.imencode(suffix, image, quality_para)[1].tofile(save_path)
    else:
        cv.imwrite(save_path, image, quality_para)

def jpeg_noise(image, para):
    encoded_img = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, para])[1]
    decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
    return decoded_img

def pil_rgb_imwrite(rgb_image, image_save_path):
    """
    [pil save a rgb image]
    Args:
        rgb_image ([np.array]): [rgb image]
        image_save_path ([str/Path]): [image save path]
    """
    pil_image = Image.fromarray(rgb_image)
    image_save_path = Path(image_save_path)
    image_save_path.parent.mkdir(parents=True, exist_ok=True)
    pil_image.save(str(image_save_path))


def image_show_from_path(file_path):
    """[show image from image file path]

    Args:
        file_path ([str or Path]): [path of image file]
    """
    assert is_path_obj(file_path) or isinstance(file_path, str)
    file_path = str(file_path)
    if not OS_exists(file_path):
        print('file: ', file_path, 'does not exist.')
    else:
        image = cv_rgb_imread(file_path)
        plt_image_show(image)


def plt_image_show(*image, window_name='image show', array_res=False, full_screen=True, cmap=None, position=[30, 30], share_xy=False, axis_off=False):
    '''
    更加鲁棒地显示图像包括二维图像,第三维度为1的图像
    '''
    image_list = list(image)
    # temp_image = extend_image_channel(image)
    image_num = len(image_list)
    col_num = int(np.ceil(image_num**0.5))
    row_num = int(np.ceil(image_num/col_num))

    if full_screen:
        if current_system() == 'Windows':
            figsize=(18.5, 9.4)
        else:
            figsize=(18.5, 9.4)

    fig, ax = plt.subplots(row_num, col_num, figsize=figsize, sharex=share_xy, sharey=share_xy)

    backend = matplotlib.get_backend()

    plt.subplots_adjust(top=0.93, bottom=0.05, left=0.05, right=0.95, hspace=0.05, wspace=0.05)

    for index, image_item in enumerate(image_list):
        x_value = None
        print_name = window_name
        if isinstance(image_item, tuple) or isinstance(image_item, list):
            assert len(image_item) == 2
            image = image_item[0]
            if isinstance(image_item[1], str):
                current_name = image_item[1]
                print_name = current_name
            elif isinstance(image_item[1], np.ndarray):
                x_value = image_item[1]
        else:
            image = image_item

        if iterable(ax):
            if ax.ndim == 1:
                cur_ax = ax[index]
            elif ax.ndim == 2:
                row_index = index // col_num
                col_index = index % col_num
                cur_ax = ax[row_index][col_index]
            else:
                raise RuntimeError(f'bad ax ndim num {ax}')
        else:
            cur_ax = ax
        if axis_off:
            cur_ax.axis('off')

        if image.ndim == 1:
            if x_value is not None and len(image) == len(x_value):
                cur_ax.plot(x_value, image)
            else:
                cur_ax.plot(image)

        else:
            if 'uint8' == image.dtype.__str__():
                cur_ax.imshow(image, cmap=cmap, vmax=np.max(image), vmin=np.min(image))
            elif 'int' in image.dtype.__str__():
                cur_ax.imshow(image, cmap=cmap, vmax=np.max(image), vmin=np.min(image))
            elif 'bool' in image.dtype.__str__():
                cur_ax.imshow(image.astype('float32'), cmap=cmap, vmax=np.max(image), vmin=np.min(image))
            elif 'float' in image.dtype.__str__():
                cur_ax.imshow((image - np.min(image)) / (max(1, np.max(image)) - np.min(image)), cmap=cmap)
            else:
                cur_ax.imshow(image.astype('uint8'), cmap=cmap, vmax=np.max(image), vmin=np.min(image))

        cur_ax.margins(0, 0)
        cur_ax.set_title(print_name)

    if not array_res:
        try:
            mngr = plt.get_current_fig_manager()
            mngr.window.wm_geometry(f"+{position[0]}+{position[1]}")
        except Exception:
            pass
        plt.show()
    else:
        image = convert_plt_to_rgb_image(plt)
        plt.close()
        return image

PIS = plt_image_show

def convert_plt_to_rgb_image(plt):
    # Convert a Matplotlib figure to a 3D numpy array with RGB channels and return it
    canvas = FigureCanvasAgg(plt.gcf())
    canvas.draw()
    w, h = canvas.get_width_height()
    buf = np.fromstring(canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)
    buf = np.roll(buf, 3, axis=2)
    image = Image.frombytes("RGBA", (w, h), buf.tostring())
    image = np.asarray(image)
    rgb_image = image[:, :, :3]
    return rgb_image


def image_formate_transfer(origin_dir, tar_dir, origin_suffix, tar_suffix, recursively=False):

    if origin_suffix.lower() not in popular_image_suffixes:
        raise Warning(f'origin_suffix {origin_suffix} is not an usually image file suffix')

    if tar_suffix.lower() not in popular_image_suffixes:
        raise Warning(f'tar_suffix {tar_suffix} is not an usually image file suffix')

    assert Path(origin_dir).is_dir(), f"origin_dir {origin_dir} does not exist"
    assert Path(tar_dir).is_dir(), f"origin_dir {tar_dir} does not exist"

    image_path_list = glob_recursively(origin_dir, origin_suffix, recursively=recursively)

    for image_path in tqdm(image_path_list, desc=f"converting suffix from {origin_suffix} to {tar_suffix}"):
        img = Image.open(image_path)
        file_name = Path(image_path).stem
        new_file_name = str(Path(tar_dir) / (file_name + '.' + tar_suffix))
        img.save(new_file_name)


def vvd_image_preprocess(image):
    """
    vvd 图像预处理
    """
    new_image = image / 127.5 - 1
    return new_image


def crop_data_around_boxes(image, crop_box, cut_box_back=False):
    """make a image crop from a image safely"""

    ndim = image.ndim
    height, width = image.shape[:2]

    crop_box = np.array(crop_box).astype('int32').tolist()

    ori_left, ori_top, ori_right, ori_bottom = 0, 0, width, height

    crop_left, crop_top, crop_right, crop_bottom = crop_box

    assert crop_right > crop_left and crop_bottom > crop_top

    crop_width = crop_right - crop_left
    crop_height = crop_bottom - crop_top

    cut_left = max(crop_left, ori_left)
    cut_right = max(min(ori_right, crop_right), cut_left)
    cut_top = max(ori_top, crop_top)
    cut_bottom = max(min(ori_bottom, crop_bottom), cut_top)

    cut_box = [cut_left, cut_top, cut_right, cut_bottom]

    crop_ori = image[cut_top:cut_bottom, cut_left:cut_right, ...]

    if cut_right - cut_left != crop_width or cut_bottom - cut_top != crop_height:

        # out of boundary
        if ndim == 3:
            crop_ori_temp = np.zeros([crop_height, crop_width, 3], dtype='uint8')
        elif ndim == 2:
            crop_ori_temp = np.zeros([crop_height, crop_width], dtype='uint8')
        else:
            raise RuntimeError(f"error image shape {image.shape} ndim {ndim}")

        win_left = cut_left - crop_left
        win_right = max(cut_right - crop_left, win_left)
        win_top = cut_top - crop_top
        win_bottom = max(cut_bottom - crop_top, win_top)

        crop_ori_temp[win_top:win_bottom, win_left:win_right, ...] = crop_ori
        crop_ori = crop_ori_temp

    if cut_box_back:
        return crop_ori, cut_box
    else:
        return crop_ori


def zero_padding(in_array, padding_size_1, padding_size_2, padding_size_3=None, padding_size_4=None):
    """
    四周补零，以此避免边界判断(仅用于三通道图像)

    输入：
    :in_array: 输入矩阵 np.array (rows, cols, 3)

    (padding_size_3-4 为 None 时)
    :padding_size_1:  上下补零行数
    :padding_size_2:  左右补零列数

    (padding_size_3-4 均不为 None 时)
    :padding_size_1:  上补零行数
    :padding_size_2:  下补零行数
    :padding_size_3:  左补零列数
    :padding_size_4:  右补零列数

    输出：
    :padded_array: 补零后的图像（新建矩阵，不修改原始输入）
    """

    assert np.ndim(in_array) == 3 or np.ndim(in_array) == 2

    if np.ndim(in_array) == 3:
        rows, cols, ndim = in_array.shape
    else:
        rows, cols = in_array.shape

    if (padding_size_3 is None) and (padding_size_4 is None):
        padding_size_1 = max(padding_size_1, 0)
        padding_size_2 = max(padding_size_2, 0)
        assert padding_size_1 >= 0 and padding_size_2 >= 0
        if np.ndim(in_array) == 3:
            padded_array = np.zeros([rows + 2 * padding_size_1, cols + 2 * padding_size_2, ndim], dtype=type(in_array[0][0][0]))
            padded_array[padding_size_1:rows + padding_size_1, padding_size_2:cols + padding_size_2, :] = in_array
        elif np.ndim(in_array) == 2:
            padded_array = np.zeros([rows + 2 * padding_size_1, cols + 2 * padding_size_2], dtype=type(in_array[0][0]))
            padded_array[padding_size_1:rows + padding_size_1, padding_size_2:cols + padding_size_2] = in_array
        else:
            raise ValueError("np.ndim error")

    else:
        assert (padding_size_3 is not None) and (padding_size_4 is not None), "padding_size_3 padding_size_4 必须都不是none"
        padding_size_1 = max(padding_size_1, 0)
        padding_size_2 = max(padding_size_2, 0)
        padding_size_3 = max(padding_size_3, 0)
        padding_size_4 = max(padding_size_4, 0)
        assert padding_size_1 >= 0 and padding_size_2 >= 0 and padding_size_3 >= 0 and padding_size_4 >= 0
        if np.ndim(in_array) == 3:
            padded_array = np.zeros([rows + padding_size_1 + padding_size_2, cols + padding_size_3 + padding_size_4, ndim], dtype=type(in_array[0][0][0]))
            padded_array[padding_size_1:rows + padding_size_1, padding_size_3:cols + padding_size_3, :] = in_array
        elif np.ndim(in_array) == 2:
            padded_array = np.zeros([rows + padding_size_1 + padding_size_2, cols + padding_size_3 + padding_size_4], dtype=type(in_array[0][0]))
            padded_array[padding_size_1:rows + padding_size_1, padding_size_3:cols + padding_size_3] = in_array
        else:
            raise ValueError("np.ndim error")

    return padded_array


def polar_move(polar_image, source_center_phase, target_center_phase):
    """[height of polar_image is the origin circle side]

    Args:
        polar_image ([np.array]): [polar image]
        source_center_phase ([float]): [source center phase]
        target_center_phase ([float]): [target center phase]
    """
    height, width = polar_image.shape[:2]
    center_index = vvd_round(source_center_phase % 360 / 360 * height)
    target_index = vvd_round(target_center_phase % 360 / 360 * height)

    new_polar_image = np.zeros_like(polar_image)

    movement = target_index - center_index

    new_polar_image[:movement] = polar_image[-movement:]
    new_polar_image[movement:] = polar_image[:-movement]

    return new_polar_image


def cycle_move(data: np.ndarray, offset: int, axis=0):
    assert axis < data.ndim
    index_list = list(range(data.ndim))
    index_list[axis] = 0
    index_list[0] = axis
    new_data = np.transpose(data, index_list)
    offset = offset % new_data.shape[0]
    if data.ndim > 1:
        concate_fun = np.vstack
    else:
        concate_fun = np.concatenate
    moved_data = concate_fun([new_data[offset:,...], new_data[:offset,...]])
    moved_data = np.transpose(moved_data, index_list)
    return moved_data


def crop_by_cycle_y_min_max(image, y_min, y_max):
    height = image.shape[0]

    if image.ndim > 1:
        concate_fun = np.vstack
    else:
        concate_fun = np.concatenate

    if y_min >= 0 and y_max <= height:
        if y_min <= y_max:
            crop_image = image[y_min:y_max, ...]
        else:
            crop_image = concate_fun((image[y_min:, ...], image[:y_max, ...]))

    elif y_min < 0:
        crop_image = concate_fun((image[y_min % height:, ...], image[:y_max, ...]))
    elif y_max > height:
        crop_image = concate_fun((image[y_min:, ...], image[:y_max % height, ...]))
    return crop_image


def crop_by_cycle_x_min_max(image, x_min, x_max):
    width = image.shape[1]

    if x_min >= 0 and x_max <= width:
        if x_min <= x_max:
            crop_image = image[:, x_min:x_max, ...]
        else:
            crop_image = np.hstack((image[:, x_min:, ...], image[:, :x_max, ...]))
    elif x_min < 0:
        crop_image = np.hstack((image[:, x_min % width:, ...], image[:, :x_max, ...]))
    elif x_max > width:
        crop_image = np.hstack((image[:, x_min:, ...], image[:, :x_max % width, ...]))
    return crop_image


def fill_sector(image, center, radius_out, radius_in, start_radian, end_radian, color=[255, 255, 255]):
    """[fill sector]

    Args:
        image ([np.array]): [input image]
        center ([list]): [center X Y]
        radius_out ([number]): [outside radius]
        radius_in ([number]): [inside radius]
        start_radian ([float]): [start radian]
        end_radian ([float]): [end radian]
        color (list, optional): [fill color]. Defaults to [255, 255, 255].

    Returns:
        [np.array]: [output image]
    """
    image = image.copy()
    mask = np.zeros_like(image)
    start_angle = start_radian / np.pi * 180
    end_angle = end_radian / np.pi * 180
    mask = cv2.ellipse(mask, vvd_round(center), vvd_round([radius_out, radius_out]), 0, start_angle, end_angle, color, -1)
    mask = cv2.ellipse(mask, vvd_round(center), vvd_round([radius_in, radius_in]), 0, start_angle, end_angle, [0] * 3, -1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones([3,3]))

    image[mask > 0] = mask[mask > 0]
    return image


def local_normalization(image, k_size=5):
    gauss_image = cv2.GaussianBlur(image, (k_size, k_size), 0)
    reduce_mean_image = image - gauss_image.astype('float')
    square_image = (reduce_mean_image ** 2)
    gauss_square_image = cv2.GaussianBlur(square_image, (k_size, k_size), 0)
    sigma_image = gauss_square_image ** 0.5
    res_image = reduce_mean_image / (sigma_image + 1e-6)

    return res_image


def get_polygons_from_mask(mask):
    """ get polygons for all isolated areas on fg-mask
        return something like: [[x1,y1], [x2,y2], [x3,y3], ...]
    """
    mask = to_gray_image(mask)
    contours, _  = cv2.findContours((mask).astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def draw_polygons(mask, polygons, color=None, thickness=5, fill=False):
    mask = mask.copy()
    if color is None:
        color = [255, 255, 255]
    if np.array(polygons).ndim == 2:
        polygons = [polygons]
    if fill:
        mask = cv2.fillPoly(mask, [np.array(p).astype('int32') for p in polygons], color)
    else:
        mask = cv2.polylines(mask, [np.array(p).astype('int32') for p in polygons], True, color=color, thickness=thickness)

    return mask

def draw_boxes(image, bboxes, color=None, thickness=5, fill=False):
    image = image.copy()
    if color is None:
        color = [255, 255, 255]
    if np.array(bboxes).ndim == 1:
        bboxes = [bboxes]
    if fill:
        thickness = -1
    for box in bboxes:
        box = vvd_round(box)
        image = cv2.rectangle(image, box[:2], box[2:4], color, thickness)
    return image


def get_xyxys_from_mask(mask):
    """ get xyxys for all isolated areas on fg-mask """
    contours = get_polygons_from_mask(mask)
    xyxys = list()
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        xyxys.append([x,y,x+w,y+h])
    return xyxys


def get_polar_ring(image, center, outer_radius, inner_radius=0, factor=1):
    size_X = vvd_round(outer_radius)
    size_Y = vvd_round(outer_radius * 2 * np.pi)
    
    dsize = [size_X, size_Y]
    center = vvd_round(center)
    ori_polar = cv2.warpPolar(image, dsize, center, size_X, 12)
    band = ori_polar[:, vvd_round(inner_radius):, ...]
    if factor != 1:
        band = image_resize(band, factor=factor)
    return band


def apply_gimp_brightness_contrast(input_img, brightness = 0, contrast = 0):
    """
    Gimp style brightness and contrast adjusification
    bringhtness: [-127, 127] --> [dark, bright]
    contrast: [-127, 127]  --> [low contrast, high contrast]
    """
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

def connected_filter(image, min_area=0, w_h_ratio=None, largest_num=None, w_min=None, w_max=None, h_min=None, h_max=None):
    image = to_gray_image(image)
    image = (image != 0).astype('uint8')
    num, mark_img, info, _ = cv2.connectedComponentsWithStats(image)
    if 0 < min_area < 1:
        min_area = min_area * time_reduce(*image.shape[:2])
    if largest_num is not None and num > 1:
        largest_num = max(0, min(vvd_round(largest_num), num - 1))
        pixel_array = info[:, -1][1:]
        index_array, _ = get_Several_MinMax_Array(pixel_array, -largest_num)
        index_array += 1
    else:
        index_array = np.nonzero(info[:, -1] > min_area)[0]
    ratio_check = False
    if w_h_ratio is not None:
        min_ratio = np.min(w_h_ratio)
        max_ratio = np.max(w_h_ratio)
        ratio_check = True
    for index in index_array:
        if index > 0:
            if ratio_check:
                sub_info = info[index]
                if min_ratio <= sub_info[2] / max(1, sub_info[3]) <= max_ratio:
                    pass
                else:
                    continue
                if w_min is not None:
                    if sub_info[2] < w_min:
                        continue
                if w_max is not None:
                    if sub_info[2] > w_max:
                        continue
                if h_min is not None:
                    if sub_info[3] < h_min:
                        continue
                if h_max is not None:
                    if sub_info[3] > h_max:
                        continue
            mark_img[mark_img == index] = - index
    res_img = (mark_img < 0).astype('uint8')
    return res_img


def close_connected_area(image, convex=False):
    image = to_gray_image(image)
    image = (image != 0).astype('uint8')
    num, mark_img, info, _ = cv2.connectedComponentsWithStats(image)
    for index in range(num):
        if index > 0:
            contours, hierarchy = cv2.findContours((mark_img == index).astype('uint8'), 2, 1)
            if convex:
                contours = cv2.convexHull(np.vstack(contours), clockwise=True).squeeze()
                if contours.ndim > 1:
                    image = cv2.fillConvexPoly(image, np.vstack(contours), (1, 1, 1))
            else:
                for contour in contours:
                    image = cv2.fillConvexPoly(image, contour, (1, 1, 1))
    return image


def get_convexHull(mask):
    contours, _ = cv2.findContours((mask != 0).astype('uint8'), 2, 1)
    convexHull_points = cv2.convexHull(np.vstack(contours), clockwise=True).squeeze()
    return convexHull_points


def bounding_bbox(mask):
    x, y, w, h =  cv2.boundingRect(get_convexHull(mask))
    bbox = [x, y, x + w, y + h]
    return bbox


def get_kernal(ksize, shape='rec'):
    """
    ksize = [W, H]
    shape in ['rec', 'circle', 'cross']
    """

    if is_number(ksize):
        ksize = [ksize, ksize]

    assert len(ksize) == 2 
    ksize = vvd_round(ksize)
    assert np.min(ksize) > 0, f"kernal size should be > 0, {ksize}"

    if shape not in ['rec', 'circle', 'cross']:
        shape = 'rec'
    if shape == 'rec':
        flag = cv2.MORPH_RECT
    elif shape == 'circle':
        flag = cv2.MORPH_ELLIPSE
    elif shape == 'cross':
        flag = cv2.MORPH_CROSS
    else:
        raise RuntimeError('unknown shape {shape}')
    
    kernal = cv2.getStructuringElement(flag, ksize)
    return kernal


def morphology_op(image, op, kernal_size, kermal_type=None):
    """
    op in ['open', 'close', 'eroid', 'dilate']
    ksize = [W, H]
    kermal_type in ['rec', 'circle', 'cross']
    """
    op_list = ['open', 'close', 'eroid', 'dilate']
    assert op in op_list, f"op {op} not in {op_list}"
    image = (image != 0).astype('uint8')
    kernal = get_kernal(kernal_size, shape=kermal_type)
    if op == 'open':
        op_mark = cv2.MORPH_OPEN
    elif op == 'close':
        op_mark = cv2.MORPH_CLOSE
    elif op == 'eroid':
        op_mark = cv2.MORPH_ERODE
    elif op == 'dilate':
        op_mark = cv2.MORPH_DILATE
    else:
        raise RuntimeError(f"unknown op mark {op_mark}")

    return cv2.morphologyEx(image, op_mark, kernal)
    


def eroid_op(image, kernal_size, kermal_type=None):
    """
    ksize = [W, H]
    kermal_type in ['rec', 'circle', 'cross']
    """
    return morphology_op(image, 'eroid', kernal_size, kermal_type)


def dilate_op(image, kernal_size, kermal_type=None):
    """
    ksize = [W, H]
    kermal_type in ['rec', 'circle', 'cross']
    """
    return morphology_op(image, 'dilate', kernal_size, kermal_type)


def open_op(image, kernal_size, kermal_type=None):
    """
    ksize = [W, H]
    kermal_type in ['rec', 'circle', 'cross']
    """
    return morphology_op(image, 'open', kernal_size, kermal_type)


def close_op(image, kernal_size, kermal_type=None):
    """
    ksize = [W, H]
    kermal_type in ['rec', 'circle', 'cross']
    """
    return morphology_op(image, 'close', kernal_size, kermal_type)