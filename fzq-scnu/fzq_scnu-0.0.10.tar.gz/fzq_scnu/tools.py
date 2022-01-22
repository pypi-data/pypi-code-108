import os
import logging
import math
import pygame


# 日志
class Logging:
    def __init__(self, images_path_logger):
        logging.basicConfig(filename=images_path_logger + 'emulator_logging.txt',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(module)s; %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=30)


# 检测矩形碰撞
def a_collide_rect_bs(surface_rect, test_rect):
    # if len(args) > 0:
    #     for arg in args:
    if surface_rect.colliderect(test_rect):
        return True, test_rect
    else:
        return False, surface_rect
    # return False, surface_rect


# 计算两点距离
def distance_ab(a, b):
    dis = math.sqrt(pow(a[0]-b[0], 2) + pow(a[1]-b[1], 2))
    return dis


def dfs_file_search(dict_name):
    import os
    # list.pop() list.append()这两个方法就可以实现栈维护功能
    stack = []
    result_txt = []
    stack.append(dict_name)
    while len(stack) != 0:  # 栈空代表所有目录均已完成访问
        temp_name = stack.pop()
        try:
            temp_name2 = os.listdir(temp_name)  # list ["","",...]
            for eve in temp_name2:
                stack.append(temp_name + "\\" + eve)  # 维持绝对路径的表达
        except NotADirectoryError:
            result_txt.append(temp_name)
    return result_txt
# a = DFS_file_search('C:\\Users\\86137\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages\\fzq_scnu')
# print(a)
# for b in a:
#     if 'fzrunner' in b:
#         print(b)


# 修改路径
def path_processing(path, countdown=-1, rep_path=''):
    trun_path = ''
    if countdown < 0:
        if '\\' in path:
            path_list = path.split('\\')
            path_list = path_list[:countdown]
            for i in path_list:
                trun_path += i + '\\\\'
            if '\\' in rep_path:
                trun_path += rep_path + '\\'
            else:
                trun_path += rep_path
        elif '/' in path:
            path_list = path.split('/')
            path_list = path_list[:countdown]
            for i in path_list:
                trun_path += i + '/'
            trun_path += rep_path
    elif countdown >= 0:
        raise Exception("path_processing的输入countdown应为负数")
    return trun_path

# print(path_processing('C:\\Users\\86137\\Documents\\python_code\\fzq_test\\files\\', -1, 'images\\'))
# print(path_processing('C:\\Users\\86137\\Documents\\python_code\\fzq_test\\files', -1, 'images.png'))


# rect矩形切割（截图）
def clip_image(rect=(0, 0, 0, 0)):
    screen_all = pygame.display.get_surface()
    image = screen_all.subsurface(rect).copy()
    image_rect = image.get_rect()
    return image, image_rect


# PIL，Surface图像类型转cv2的ndarray类型，并改变图像大小
def change_image(pygame_image, size=(100, 100)):
    from PIL import Image
    import cv2
    import numpy as np
    if type(pygame_image).__name__ == 'Surface':
        pil_string_image = pygame.image.tostring(pygame_image, "RGB", False)  # 将当前图像输出为字符变量
        pil_image = Image.frombytes('RGB', pygame_image.get_size(), pil_string_image, 'raw')  # 将字符变量变为Image变量
        pil_image = pil_image.resize(size, resample=Image.BOX)  # 改变尺寸
        cv2_img = cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2BGR)  # pil转cv2类型
        return cv2_img
    elif type(pygame_image).__name__ == 'Image':
        pil_image = pygame_image.resize(size, resample=Image.BOX)  # 改变尺寸
        cv2_img = cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2BGR)  # pil转cv2类型
        return cv2_img
    elif type(pygame_image).__name__ == 'ndarray':
        cv2_img = cv2.resize(pygame_image, size)
        return cv2_img
    elif pygame_image == 'None':
        pass
    else:
        raise Exception("输入图像类型不正确或其他错误")


# 载入图像（用处不大）
def load_graphics(path, accept=('.img', '.png', '.bsp', '.gif')):
    graphics = {}
    for pic in os.listdir(path):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
            graphics[name] = img
    return graphics

# def future_matching():
#     # ORB算法实现特征检测+暴力匹配
#     import cv2, os
#     from matplotlib import pyplot as plt
#     import PySide2
#     dirname = os.path.dirname(PySide2.__file__)
#     plugin_path = os.path.join(dirname, 'plugins', 'platforms')
#     os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
#
#     # 读取图片内容
#     img1 = cv2.imread('5279997.jpg', 0)
#     img2 = cv2.imread('miaomiao.png', 0)
#     # 使用ORB特征检测器和描述符，计算关键点和描述符
#     orb = cv2.ORB_create()
#     kp1, des1 = orb.detectAndCompute(img1, None)
#     kp2, des2 = orb.detectAndCompute(img2, None)
#     # 暴力匹配BFMatcher，遍历描述符，确定描述符是否匹配，然后计算匹配距离并排序
#     # BFMatcher函数参数：
#     # normType：NORM_L1, NORM_L2, NORM_HAMMING, NORM_HAMMING2。
#     # NORM_L1和NORM_L2是SIFT和SURF描述符的优先选择，
#     # NORM_HAMMING和NORM_HAMMING2是用于ORB算法
#     bf = cv2.BFMatcher(normType=cv2.NORM_HAMMING, crossCheck=True)
#     matches = bf.match(des1, des2)
#     matches = sorted(matches, key=lambda x: x.distance)
#     # matches是DMatch对象，具有以下属性：
#     # DMatch.distance - 描述符之间的距离。 越低越好。
#     # DMatch.trainIdx - 训练描述符中描述符的索引
#     # DMatch.queryIdx - 查询描述符中描述符的索引
#     # DMatch.imgIdx - 训练图像的索引。
#     # 使用plt将两个图像的匹配结果显示出来
#     print(len(matches))
#     img3 = cv2.drawMatches(img1=img1,
#                            keypoints1=kp1,
#                            img2=img2,
#                            keypoints2=kp2,
#                            matches1to2=matches,
#                            outImg=img2,
#                            flags=2)
#     plt.imshow(img3)
#     plt.show()
