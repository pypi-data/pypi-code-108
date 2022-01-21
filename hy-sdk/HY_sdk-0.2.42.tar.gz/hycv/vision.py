import cv2
from PIL import Image
import numpy as np
"""
 接下来的开发灵感：
 - upload.sh增加文件夹自动删除功能
 - mtcnn增加68点人脸检测模块
"""


def ChangeImageDPI(input_path, output_path, dpi=300):
    """
    改变输入图像的dpi.
    input_path: 输入图像路径
    output_path: 输出图像路径
    dpi：打印分辨率
    """
    image = Image.open(input_path)
    image.save(output_path, dpi=(dpi, dpi))
    print(1)
    print("Your Image's DPI have been changed. The last DPI = ({},{}) ".format(dpi,dpi))


def IDphotos_cut(x1, y1, x2, y2, img):
    """
    在图片上进行滑动裁剪,输入输出为
    输入：一张图片img,和裁剪框信息(x1,x2,y1,y2)
    输出: 裁剪好的图片,然后裁剪框超出了图像范围,那么将用0矩阵补位
    ------------------------------------
    x:裁剪框左上的横坐标
    y:裁剪框左上的纵坐标
    x2:裁剪框右下的横坐标
    y2:裁剪框右下的纵坐标
    crop_size:裁剪框大小
    img:裁剪图像（numpy.array）
    output_path:裁剪图片的输出路径
    ------------------------------------
    """

    crop_size = (y2-y1, x2-x1)
    """
    ------------------------------------
    temp_x_1:裁剪框左边超出图像部分
    temp_y_1:裁剪框上边超出图像部分
    temp_x_2:裁剪框右边超出图像部分
    temp_y_2:裁剪框下边超出图像部分
    ------------------------------------
    """
    temp_x_1 = 0
    temp_y_1 = 0
    temp_x_2 = 0
    temp_y_2 = 0

    if y1 < 0:
        temp_y_1 = abs(y1)
        y1 = 0
    if y2 > img.shape[0]:
        temp_y_2 = y2
        y2 = img.shape[0]
        temp_y_2 = temp_y_2 - y2

    if x1 < 0:
        temp_x_1 = abs(x1)
        x1 = 0
    if x2 > img.shape[1]:
        temp_x_2 = x2
        x2 = img.shape[1]
        temp_x_2 = temp_x_2 - x2

    # 生成一张全透明背景
    background = np.ones((crop_size[0], crop_size[1], 4)) * (255, 255, 255, 0)
    background[temp_y_1: crop_size[0] - temp_y_2, temp_x_1: crop_size[1] - temp_x_2] = img[y1:y2, x1:x2]

    return background


def resize_image_esp(input_image, esp=2000):
    """
    输入：
    input_path：numpy图片
    esp：限制的最大边长
    """
    # resize函数=>可以让原图压缩到最大边为esp的尺寸(不改变比例)
    width = input_image.shape[0]

    length = input_image.shape[1]
    max_num = max(width, length)

    if max_num > esp:
        print("Image resizing...")
        if width == max_num:
            length = int((esp / width) * length)
            width = esp

        else:
            width = int((esp / length) * width)
            length = esp
        print(length, width)
        im_resize = cv2.resize(input_image, (length, width), interpolation=cv2.INTER_AREA)
        return im_resize
    else:
        return input_image


def detect_distance(value, crop_heigh, max=0.06, min=0.04):
    """
    检测人头顶与照片顶部的距离是否在适当范围内。
    输入：与顶部的差值
    输出：(status, move_value)
    status=0 不动
    status=1 人脸应向上移动（裁剪框向下移动）
    status-2 人脸应向下移动（裁剪框向上移动）
    ---------------------------------------
    value：头顶与照片顶部的距离
    crop_heigh: 裁剪框的高度
    max: 距离的最大值
    min: 距离的最小值
    ---------------------------------------
    """
    value = value/crop_heigh  # 头顶往上的像素占图像的比例
    print("value:", value)
    if min <= value <= max:
        return 0, 0
    elif value > max:
        # 头顶往上的像素比例高于max
        move_value = value - max
        move_value = int(move_value * crop_heigh)
        # print("上移{}".format(move_value))
        return 1, move_value
    else:
        # 头顶往上的像素比例低于min
        move_value = min - value
        move_value = int(move_value * crop_heigh)
        # print("下移{}".format(move_value))
        return 2, move_value


def draw_picture_dots(image, dots, pen_size=10, pen_color=(0, 0, 255)):
    """
    给一张照片上绘制点。
    image: Opencv图像矩阵
    dots: 一堆点,形如[(100,100),(150,100)]
    pen_size: 画笔的大小
    pen_color: 画笔的颜色
    """
    if isinstance(dots, dict):
        dots = [v for u, v in dots.items()]
    image = image.copy()
    for x, y in dots:
        cv2.circle(image, (int(x), int(y)), pen_size, pen_color, -1)
    return image


def draw_picture_rectangle(image, bbox, pen_size=2, pen_color=(0, 0, 255)):
    image = image.copy()
    x1 = int(bbox[0])
    y1 = int(bbox[1])
    x2 = int(bbox[2])
    y2 = int(bbox[3])
    cv2.rectangle(image, (x1,y1), (x2, y2), pen_color, pen_size)
    return image


def add_background(input_image, bgr=(0, 0, 0), new_background=None):
    height, width = input_image.shape[0], input_image.shape[1]
    b, g, r, a = cv2.split(input_image)
    if new_background is None:
        background = np.array([[[bgr[0], bgr[1], bgr[2]]]])
        background = np.resize(background, (height, width, 3))
    else:
        background = new_background
        background = cv2.resize(background, (width, height))
    # print(background.shape)

    b2, g2, r2 = cv2.split(background)
    output = np.ones((height, width, 3))
    output[:, :, 0] = b * (a / 255) + b2 * (1 - a / 255)
    output[:, :, 1] = g * (a / 255) + g2 * (1 - a / 255)
    output[:, :, 2] = r * (a / 255) + r2 * (1 - a / 255)

    return output


def cover_image(image, background, x, y, mode=1):
    """
    mode = 1: directly cover
    mode = 2: cv2.add
    mode = 3: bgra cover
    """
    image = image.copy()
    background = background.copy()
    height1, width1 = background.shape[0], background.shape[1]
    height2, width2 = image.shape[0], image.shape[1]
    wuqiong_bg_y = height1 + 1
    wuqiong_bg_x = width1 + 1
    wuqiong_img_y = height2 + 1
    wuqiong_img_x = width2 + 1

    def cover_mode(image, background, imgy1=0, imgy2=-1, imgx1=0, imgx2=-1, bgy1=0, bgy2=-1, bgx1=0, bgx2=-1, mode=1):
        if mode == 1:
            background[bgy1:bgy2, bgx1:bgx2] = image[imgy1:imgy2, imgx1:imgx2]
        elif mode == 2:
            background[bgy1:bgy2, bgx1:bgx2] = cv2.add(background[bgy1:bgy2, bgx1:bgx2], image[imgy1:imgy2, imgx1:imgx2])
        elif mode == 3:
            b, g, r, a = cv2.split(image[imgy1:imgy2, imgx1:imgx2])
            b2, g2, r2, a2 = cv2.split(background[bgy1:bgy2, bgx1:bgx2])
            background[bgy1:bgy2, bgx1:bgx2, 0] = b * (a / 255) + b2 * (1 - a / 255)
            background[bgy1:bgy2, bgx1:bgx2, 1] = g * (a / 255) + g2 * (1 - a / 255)
            background[bgy1:bgy2, bgx1:bgx2, 2] = r * (a / 255) + r2 * (1 - a / 255)
            background[bgy1:bgy2, bgx1:bgx2, 3] = cv2.add(a, a2)

        return background

    if x >= 0 and y >= 0:
        x2 = x + width2
        y2 = y + height2

        if x2 <= width1 and y2 <= height1:
            background = cover_mode(image, background,0,wuqiong_img_y,0,wuqiong_img_x,y,y2,x,x2,mode)

        elif x2 > width1 and y2 <= height1:
            # background[y:y2, x:] = image[:, :width1 - x]
            background = cover_mode(image, background, 0, wuqiong_img_y, 0, width1-x, y, y2, x, wuqiong_bg_x,mode)

        elif x2 <= width1 and y2 > height1:
            # background[y:, x:x2] = image[:height1 - y, :]
            background = cover_mode(image, background, 0, height1-y, 0, wuqiong_img_x, y, wuqiong_bg_y, x, x2,mode)
        else:
            # background[y:, x:] = image[:height1 - y, :width1 - x]
            background = cover_mode(image, background, 0, height1-y, 0, width1-x, y, wuqiong_bg_y, x, wuqiong_bg_x,mode)

    elif x < 0 and y >= 0:
        x2 = x + width2
        y2 = y + height2

        if x2 <= width1 and y2 <= height1:
            # background[y:y2, :x + width2] = image[:, abs(x):]
            background = cover_mode(image, background, 0, wuqiong_img_y, abs(x), wuqiong_img_x, y, y2, 0, x+width2,mode)
        elif x2 > width1 and y2 <= height1:
            background = cover_mode(image, background, 0, wuqiong_img_y, abs(x), width1+abs(x), y, y2, 0, wuqiong_bg_x,mode)
        elif x2 <= 0:
            pass
        elif x2 <= width1 and y2 > height1:
            background = cover_mode(image, background, 0, height1-y, abs(x), wuqiong_img_x, y, wuqiong_bg_y, 0, x2, mode)
        else:
            # background[y:, :] = image[:height1 - y, abs(x):width1 + abs(x)]
            background = cover_mode(image, background, 0, height1-y, abs(x), width1+abs(x), y, wuqiong_bg_y, 0, wuqiong_bg_x,mode)

    elif x >= 0 and y < 0:
        x2 = x + width2
        y2 = y + height2
        if y2 <= 0:
            pass
        if x2 <= width1 and y2 <= height1:
            # background[:y2, x:x2] = image[abs(y):, :]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, 0, wuqiong_img_x, 0, y2, x, x2,mode)
        elif x2 > width1 and y2 <= height1:
            # background[:y2, x:] = image[abs(y):, :width1 - x]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, 0, width1-x, 0, y2, x, wuqiong_bg_x,mode)
        elif x2 <= width1 and y2 > height1:
            # background[:, x:x2] = image[abs(y):height1 + abs(y), :]
            background = cover_mode(image, background, abs(y), height1+abs(y), 0, wuqiong_img_x, 0, wuqiong_bg_y, x, x2,mode)
        else:
            # background[:, x:] = image[abs(y):height1 + abs(y), :width1 - abs(x)]
            background = cover_mode(image, background, abs(y), height1+abs(y), 0, width1-abs(x), 0, wuqiong_bg_x, x, wuqiong_bg_x,mode)

    else:
        x2 = x + width2
        y2 = y + height2
        if y2 <= 0 or x2 <= 0:
            pass
        if x2 <= width1 and y2 <= height1:
            # background[:y2, :x2] = image[abs(y):, abs(x):]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, abs(x), wuqiong_img_x, 0, y2, 0, x2,mode)
        elif x2 > width1 and y2 <= height1:
            # background[:y2, :] = image[abs(y):, abs(x):width1 + abs(x)]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, abs(x), width1+abs(x), 0, y2, 0, wuqiong_bg_x,mode)
        elif x2 <= width1 and y2 > height1:
            # background[:, :x2] = image[abs(y):height1 + abs(y), abs(x):]
            background = cover_mode(image, background, abs(y), height1+abs(y), abs(x), wuqiong_img_x, 0, wuqiong_bg_y, 0, x2,mode)
        else:
            # background[:, :] = image[abs(y):height1 - abs(y), abs(x):width1 + abs(x)]
            background = cover_mode(image, background, abs(y), height1-abs(y), abs(x), width1+abs(x), 0, wuqiong_bg_y, 0, wuqiong_bg_x,mode)

    return background


def image2bgr(input_image):
    if len(input_image.shape) == 2:
        input_image = input_image[:, :, None]
    if input_image.shape[2] == 1:
        result_image = np.repeat(input_image, 3, axis=2)
    elif input_image.shape[2] == 4:
        result_image = input_image[:, :, 0:3]
    else:
        result_image = input_image

    return result_image


if __name__ == "__main__":
    image = cv2.imread("./03.png", -1)
    result_image = add_background(image, bgr=(255, 255, 255))
    cv2.imwrite("test.jpg", result_image)