"""
本文件存放一些自制的简单的图像处理函数
"""
from PIL import Image
import cv2
import numpy as np
import math
import warnings
import csv
import glob


def cover_mask(image_path, mask_path, alpha=0.85, rate=0.1, if_save=True):
    """
    在图片右下角盖上水印
    :param image_path:
    :param mask_path: 水印路径，以PNG方式读取
    :param alpha： 不透明度，默认为0.85
    :param rate： 水印比例，越小水印也越小，默认为0.1
    :param if_save: 是否将裁剪后的图片保存，如果为True，则保存并返回新图路径，否则不保存，返回截取后的图片对象
    :return: 新的图片路径
    """
    # 生成新的图片路径，我们默认图片后缀存在且必然包含“.”
    path_len = len(image_path)
    index = 0
    for index in range(path_len - 1, -1, -1):
        if image_path[index] == ".":
            break
        if 3 >= path_len - index >= 6:
            raise TypeError("输入的图片格式有误！")
    new_path = image_path[0:index] + "_with_mask" + image_path[index:path_len]
    # 以png方式读取水印图
    mask = Image.open(mask_path).convert('RGBA')
    mask_h, mask_w = mask.size
    # 以png的方式读取原图
    im = Image.open(image_path).convert('RGBA')
    # 我采取的策略是，先拷贝一张原图im为base作为基底，然后在im上利用paste函数添加水印
    # 此时的水印是完全不透明的，我需要利用blend函数内置参数alpha进行不透明度调整
    base = im.copy()
    # layer = Image.new('RGBA', im.size, (0, 0, 0, ))
    # tmp = Image.new('RGBA', im.size, (0, 0, 0, 0))
    h, w = im.size
    # 根据原图大小缩放水印图
    mask = mask.resize((int(rate*math.sqrt(w*h*mask_h/mask_w)), int(rate*math.sqrt(w*h*mask_w/mask_h))), Image.ANTIALIAS)
    mh, mw = mask.size
    r, g, b, a = mask.split()
    im.paste(mask, (h-mh, w-mw), mask=a)
    # im.show()
    out = Image.blend(base, im, alpha=alpha).convert('RGB')
    # out = Image.alpha_composite(im, layer).convert('RGB')
    if if_save:
        out.save(new_path)
        return new_path
    else:
        return out

def check_image(image) ->np.ndarray:
    """
    判断某一对象是否为图像/矩阵类型，最终返回图像/矩阵
    """
    if not isinstance(image, np.ndarray):
        image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    return image

def get_box(image) -> list:
    """
    这是一个简单的扣图后图像定位函数，不考虑噪点影响
    我们使用遍历的方法，碰到非透明点以后立即返回位置坐标
    :param image:图像信息，可以是图片路径，也可以是已经读取后的图像
    如果传入的是图片路径，我会首先通过读取图片、二值化，然后再进行图像处理
    如果传入的是图像，直接处理，不会二值化
    :return: 回传一个列表，分别是图像的上下（y）左右（x）自个值
    """
    image = check_image(image)
    height, width, _ = image.shape
    try:
        b, g, r, a = cv2.split(image)
        # 二值化处理
        a = (a > 127).astype(np.int_)
    except ValueError:
        # 说明传入的是无透明图层的图像，直接返回图像尺寸
        warnings.warn("你传入了一张非四通道格式的图片！")
        return [0, height, 0, width]
    flag1, flag2 = 0, 0
    box = [0, 0, 0, 0]  # 上下左右
    # 采用两面夹击战术，使用flag1和2确定两面的裁剪程度
    # 先得到上下
    for i in range(height):
        for j in range(width):
            if flag1 == 0 and a[i][j] != 0:
                flag1 = 1
                box[0] = i
            if flag2 == 0 and a[height - i -1][j] != 0:
                flag2 = 1
                box[1] = height - i - 1
        if flag2 * flag1 == 1:
            break
    # 再得到左右
    flag1, flag2 = 0, 0
    for j in range(width):
        for i in range(height):
            if flag1 == 0 and a[i][j] != 0:
                flag1 = 1
                box[2] = j
            if flag2 == 0 and a[i][width - j - 1] != 0:
                flag2 = 1
                box[3] = width - j - 1
        if flag2 * flag1 == 1:
            break
    return box

def filtering(img, f, x, y, x_max, y_max, x_min, y_min, area=0, noise_size=50) ->tuple:
    """
    filtering将使用递归的方法得到一个连续图像（这个连续矩阵必须得是单通道的）的范围(坐标)
    :param img: 传入的矩阵
    :param f: 和img相同尺寸的全零矩阵，用于标记递归递归过的点
    :param x: 当前递归到的x轴坐标
    :param y: 当前递归到的y轴坐标
    :param x_max: 递归过程中x轴坐标的最大值
    :param y_max: 递归过程中y轴坐标的最大值
    :param x_min: 递归过程中x轴坐标的最小值
    :param y_min: 递归过程中y轴坐标的最小值
    :param area: 当前递归区域面积大小
    :param noise_size: 最大递归区域面积大小，当area大于noise_size时，函数返回(0, 1)
    :return: 分两种情况，当area大于noise_size时，函数返回(0, 1)，当area小于等于noise_size时，函数返回(box, 0)
            其中box是连续图像的坐标和像素点面积（上下左右，面积）
    理论上来讲，我们可以用这个函数递归出任一图像的形状和坐标，但是从计算机内存、计算速度上考虑，这并不是一个好的选择
    所以这个函数一般用于判断和过滤噪点
    """
    dire_dir = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, -1), (-1, 1)]
    height, width = img.shape
    f[x][y] = 1
    for dire in dire_dir:
        delta_x, delta_y = dire
        tmp_x, tmp_y = (x + delta_x, y + delta_y)
        if height > tmp_x >= 0 and width > tmp_y >= 0:
            if img[tmp_x][tmp_y] != 0 and f[tmp_x][tmp_y] == 0:
                f[tmp_x][tmp_y] = 1
                # cv2.imshow("test", f)
                # cv2.waitKey(3)
                area += 1
                if area > noise_size:
                    return 0, 1
                else:
                    x_max = tmp_x if tmp_x > x_max else x_max
                    x_min = tmp_x if tmp_x < x_min else x_min
                    y_max = tmp_y if tmp_y > y_max else y_max
                    y_min = tmp_y if tmp_y < y_min else y_min
                    box, flag = filtering(img, f, tmp_x, tmp_y, x_max, y_max, x_min, y_min, area=area, noise_size=noise_size)
                    if flag == 1:
                        return 0, 1
                    else:
                        (x_max, x_min, y_max, y_min, area) = box
    return [x_min, x_max, y_min, y_max, area], 0

def get_box_pro(image, model=1, correction_factor:int=1) ->list:
    """
    相比于get_box,本函数新增抗噪点特性.
    下面的四个函数是用于模块简洁化的，本身没有实质意义
    """
    def low_to_high(img, flag=0):
        xlow = 0
        height, width = img.shape
        tmp = np.zeros(img.shape)
        for x_low in range(height):
            for y in range(width):
                # filtering函数将会返回遍历到的非透明像素点的"box"，但是如果遍历到的非透明像素点的个数大于noise_size，则将其保留，跳出循环
                if img[x_low][y] != 0:
                    box, flag = filtering(img, tmp, x_low, y, x_low, y, x_low, y, area=1)
                    if flag == 1:
                        # 跳出循环
                        xlow = x_low + correction_factor
                        break
                    else:
                        # 跳过噪点
                        x_low = box[0]
            if flag == 1:
                break
        return xlow
    def high_to_low(img, flag=0):
        height, width = img.shape
        xhigh = height - 1
        tmp = np.zeros(img.shape)
        for x_high in range(height - 1, -1, -1):
            for y in range(width):
                if img[x_high][y] != 0:
                    box, flag = filtering(img, tmp, x_high, y, x_high, y, x_high, y, area=1)
                    if flag == 1:
                        # 跳出循环
                        xhigh = x_high - correction_factor
                        break
                    else:
                        # 跳过噪点
                        x_high = box[1]
            if flag == 1:
                break
        return xhigh
    def left_to_right(img, flag=0):
        # 左右的不用考虑羽化
        height, width = img.shape
        yleft = 0
        tmp = np.zeros(img.shape)
        for y_left in range(width):
            for x in range(height):
                if img[x][y_left] != 0:
                    box, flag = filtering(img, tmp, x, y_left, x, y_left, x, y_left, area=1)
                    if flag == 1:
                        # 跳出循环
                        yleft = y_left
                        break
                    else:
                        # 跳过噪点
                        y_left = box[2]
            if flag == 1:
                break
        return yleft
    def right_to_left(img, flag=0):
        # 左右的不用考虑羽化
        height, width = img.shape
        yright = 0
        tmp = np.zeros(img.shape)
        for y_right in range(width - 1, -1, -1):
            for x in range(height):
                if img[x][y_right] != 0:
                    box, flag = filtering(img, tmp, x, y_right, x, y_right, x, y_right, area=1)
                    if flag == 1:
                        # 跳出循环
                        yright = y_right
                        break
                    else:
                        # 跳过噪点
                        y_right = box[2]
            if flag == 1:
                break
        return yright
    image = check_image(image)
    height, width, _ = image.shape
    try:
        b, g, r, a = cv2.split(image)
        # 二值化处理
        a = (a > 127).astype(np.int_)
    except ValueError:
        # 说明传入的是无透明图层的图像，直接返回图像尺寸
        warnings.warn("你传入了一张非四通道格式的图片！")
        return [0, height, 0, width]
    # 上
    yhigh = low_to_high(a)
    # 接下来从下到上，左到右，右到左分别执行上述重复过程
    # 下
    ylow = high_to_low(a)
    # 左
    xleft = left_to_right(a)
    # 右
    xright = right_to_left(a)
    if model == 1:
        # model=1,将会返回切割出的矩形框的四个坐标点信息
        return [yhigh, ylow ,xleft, xright]
    elif model == 2:
        # model=2.将会返回矩形框四边相距于原图四边的距离
        return [yhigh, height - ylow, xleft, width - xright]
    else:
        raise EOFError("请选择正确的模式！")

def cut(image_path:str, box:list, if_save=True):
    """
    根据box，裁剪对应的图片区域后保存
    :param image_path: 原图路径
    :param box: 坐标列表，上下左右
    :param if_save：是否将裁剪后的图片保存，如果为True，则保存并返回新图路径，否则不保存，返回截取后的图片对象
    :return: 新图路径或者是新图对象
    """
    index = 0
    path_len = len(image_path)
    up, down, left, right = box
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    new_image = image[up: down, left: right]
    if if_save:
        for index in range(path_len - 1, -1, -1):
            if image_path[index] == ".":
                break
            if 3 >= path_len - index >= 6:
                raise TypeError("输入的图片格式有误！")
        new_path = image_path[0:index] + "_cut" + image_path[index:path_len]
        cv2.imwrite(new_path, new_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        return new_path
    else:
        return new_image

def zoom_image_without_change_size(image:np.ndarray, zoom_rate, interpolation=cv2.INTER_NEAREST) ->np.ndarray:
    """
    在不改变原图大小的情况下，对图像进行放大，目前只支持从图像中心放大
    :param image： 传入的图像对象
    :param zoom_rate： 放大比例，单位为倍（初始为1倍）
    :param interpolation： 插值方式，与opencv的resize内置参数相对应，默认为最近邻插值
    :return: 裁剪后的图像实例
    """
    height, width, _ = image.shape
    if zoom_rate < 1:
        # zoom_rate不能小于1
        raise ValueError("zoom_rate不能小于1！")
    height_tmp = int(height * zoom_rate)
    width_tmp = int(width * zoom_rate)
    image_tmp = cv2.resize(image, (height_tmp, width_tmp), interpolation=interpolation)
    # 定位一下被裁剪的位置，实际上是裁剪框的左上角的点的坐标
    delta_x = (width_tmp - width) // 2  # 横向
    delta_y = (height_tmp - height) // 2  # 纵向
    return image_tmp[delta_y : delta_y + height, delta_x : delta_x + width]

def filedir2csv(scan_filedir, csv_filedir):
    file_list = glob.glob(scan_filedir+"/*")

    with open(csv_filedir, "w") as csv_file:
        writter = csv.writer(csv_file)
        for file_dir in file_list:
            writter.writerow([file_dir])

    print("filedir2csv success!")

def full_ties(image_pre:np.ndarray):
    height, width = image_pre.shape
    # 先膨胀
    kernel = np.ones((5, 5), dtype=np.uint8)
    dilate = cv2.dilate(image_pre, kernel, 1)
    # cv2.imshow("dilate", dilate)
    def FillHole(image):
        # 复制 image 图像
        im_floodFill = image.copy()
        # Mask 用于 floodFill，官方要求长宽+2
        mask = np.zeros((height + 2, width + 2), np.uint8)
        seedPoint = (0, 0)
        # floodFill函数中的seedPoint对应像素必须是背景
        is_break = False
        for i in range(im_floodFill.shape[0]):
            for j in range(im_floodFill.shape[1]):
                if (im_floodFill[i][j] == 0):
                    seedPoint = (i, j)
                    is_break = True
                    break
            if (is_break):
                break
        # 得到im_floodFill 255填充非孔洞值
        cv2.floodFill(im_floodFill, mask, seedPoint, 255)
        # cv2.imshow("tmp1", im_floodFill)
        # 得到im_floodFill的逆im_floodFill_inv
        im_floodFill_inv = cv2.bitwise_not(im_floodFill)
        # cv2.imshow("tmp2", im_floodFill_inv)
        # 把image、im_floodFill_inv这两幅图像结合起来得到前景
        im_out = image | im_floodFill_inv
        return im_out
    # 洪流算法填充
    image_floodFill = FillHole(dilate)
    # 填充图和原图合并
    image_final = image_floodFill | image_pre
    # 再腐蚀
    kernel = np.ones((5, 5), np.uint8)
    erosion= cv2.erode(image_final, kernel, iterations=6)
    # cv2.imshow("erosion", erosion)
    # 添加高斯模糊
    blur = cv2.GaussianBlur(erosion, (5, 5), 2.5)
    # cv2.imshow("blur", blur)
    # image_final = merge_image(image_pre, erosion)
    # 再与原图合并
    image_final = image_pre | blur
    # cv2.imshow("final", image_final)
    return image_final

def cut_BiggestAreas(image):
    # 裁剪出整张图轮廓最大的部分
    def find_BiggestAreas(image_pre):
        # 定义一个三乘三的卷积核
        kernel = np.ones((3, 3), dtype=np.uint8)
        # 将输入图片膨胀
        # dilate = cv2.dilate(image_pre, kernel, 3)
        # cv2.imshow("dilate", dilate)
        # 将输入图片二值化
        _, thresh = cv2.threshold(image_pre, 127, 255, cv2.THRESH_BINARY)
        # cv2.imshow("thresh", thresh)
        # 将二值化后的图片膨胀
        dilate_afterThresh = cv2.dilate(thresh, kernel, 5)
        # cv2.imshow("thresh_afterThresh", dilate_afterThresh)
        # 找轮廓
        contours_, hierarchy = cv2.findContours(dilate_afterThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # 识别出最大的轮廓
        # 需要注意的是,在低版本的findContours当中返回的结果是tuple,不支持pop,所以需要将其转为pop
        contours = [x for x in contours_]
        area = map(cv2.contourArea, contours)
        area_list = list(area)
        area_max = max(area_list)
        post = area_list.index(area_max)
        # 将最大的区域保留,其余全部填黑
        contours.pop(post)
        for i in range(len(contours)):
            cv2.drawContours(image_pre, contours, i, 0, cv2.FILLED)
        # cv2.imshow("cut", image_pre)
        return image_pre
    b, g, r, a = cv2.split(image)
    a_new = find_BiggestAreas(a)
    new_image = cv2.merge((b, g, r, a_new))
    return new_image

def locate_neck(image:np.ndarray, proportion):
    """
    根据输入的图片(四通道)和proportion(自上而下)的比例,定位到相应的y点,然后向内收缩,直到两边的像素点不透明
    """
    if image.shape[-1] != 4:
        raise TypeError("请输入一张png格式的四通道图片!")
    if proportion > 1 or proportion <=0:
        raise ValueError("proportion 必须在0~1之间!")
    _, _, _, a = cv2.split(image)
    height, width = a.shape
    _, a = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)
    y = int(height * proportion)
    x = 0
    for x in range(width):
        if a[y][x] == 255:
            break
    left = (y, x)
    for x in range(width - 1, -1 , -1):
        if a[y][x] == 255:
            break
    right = (y, x)
    return left, right, right[1] - left[1]

def get_cutbox_image(input_image):
    height, width = input_image.shape[0], input_image.shape[1]
    y_top, y_bottom, x_left, x_right = get_box_pro(input_image, model=2)
    result_image = input_image[y_top:height - y_bottom, x_left:width - x_right]
    return result_image

def brightnessAdjustment(image: np.ndarray, bright_factor: int=0):
    """
    图像亮度调节
    :param image: 输入的图像矩阵
    :param bright_factor:亮度调节因子，可正可负,没有范围限制
            当bright_factor ---> +无穷 时，图像全白
            当bright_factor ---> -无穷 时，图像全黑
    :return: 处理后的图片
    """
    res = np.uint8(np.clip(np.int16(image) + bright_factor, 0, 255))
    return res

def contrastAdjustment(image: np.ndarray, contrast_factor: int = 0):
    """
    图像对比度调节,实际上调节对比度的同时对亮度也有一定的影响
    :param image: 输入的图像矩阵
    :param contrast_factor:亮度调节因子，可正可负,范围在[-100, +100]之间
            当contrast_factor=-100时，图像变为灰色
    :return: 处理后的图片
    """
    contrast_factor = 1 + min(contrast_factor, 100) / 100 if contrast_factor > 0 else 1 + max(contrast_factor,
                                                                                              -100) / 100
    image_b = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bright_ = image_b.mean()
    res = np.uint8(np.clip(contrast_factor * (np.int16(image) - bright_) + bright_, 0, 255))
    return res