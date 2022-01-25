import os, glob, random, cv2, numpy as np
import xml.etree.ElementTree as ET
from tqdm import tqdm

# from imgaugments import reset_dir



def reset_dir(filepath):
    for each_file in os.listdir(filepath):
        if each_file.startswith('imgaug_'):
            os.remove(filepath + os.sep + each_file)


def bg_treat(img_path, xml_path, imgfiles, bg_path, method_num=0, epoch=0, class_names=None):
    """
    box_list = [(cls_type_0, rect_0), (cls_type_1, rect_1), ... , (cls_type_n, rect_n)]
    rect = [x0, y0, x1, y1, x2, y2, x3, y3]  8个点的坐标，从左上-->右上-->右下-->左下的顺序提供
    left_top = (x0, y0), right_top = (x1, y1), right_bottom = (x2, y2), left_bottom = (x3, y3)
    exp_name : 增强后的图片名称所增加的前缀名称，用于区分与之前图片
    """

    def convert_annotation(filename, xml_path):
        in_file = open(xml_path + os.sep + '%s.xml' % (filename), encoding="utf-8")
        tree = ET.parse(in_file)
        root = tree.getroot()
        boxes = []
        for obj in root.iter('object'):
            # difficult = obj.find('difficult').text
            cls = obj.find('name').text
            xmlbox = obj.find('bndbox')
            b = [int(xmlbox.find('xmin').text), int(xmlbox.find('xmax').text), int(xmlbox.find('ymin').text),
                 int(xmlbox.find('ymax').text)]
            pos = [b[0], b[2], b[1], b[2], b[1], b[3], b[0], b[3]]  # 这里的目的，是为了和更换背景需求的坐标数据对应
            boxes.append((cls, pos))
        return boxes

    def change_Anno(anno_path, anno_write_path, newboxes):
        tree = ET.parse(anno_path)
        root = tree.getroot()
        size = root.find('size')
        w = int(size.find('width').text)
        objects = root.findall("object")
        for obj, (cls, rect) in zip(objects, newboxes):
            bbox = obj.find('bndbox')
            bbox.find('xmin').text = str(rect[0])
            bbox.find('xmax').text = str(rect[2])
            bbox.find('ymin').text = str(rect[1])
            bbox.find('ymax').text = str(rect[3])
        tree.write(anno_write_path)  # 保存修改后的XML文件

    # for imgfile in tqdm(glob.glob(img_path + '/*')):
    for imgfile in imgfiles:
        filename, ext = os.path.splitext(os.path.basename(imgfile))
        bgfile = random.choice(glob.glob(bg_path + "/*"))
        box_list = convert_annotation(filename, xml_path)  # 获取原始的box数据，要求按照下面的for循环的数据格式提供
        image = cv2.imread(os.path.join(img_path, imgfile))
        background = cv2.imread(bgfile)  #
        img_height, img_width = image.shape[:2]
        bg_height, bg_width = background.shape[:2]
        # resize image to background size
        resize_multiple = min(bg_height, bg_width) / max(img_height, img_width)
        image = cv2.resize(image, (int(img_width * resize_multiple), int(img_height * resize_multiple)))
        # new_h, new_w = image.shape[:2]
        # h_pos = random.randint(0, (bg_height - new_h))
        # w_pos = random.randint(0, (bg_width - new_w))

        # calculate the boxes after adding background
        new_boxes = []
        for cls_type, rect in box_list:
            for coor_index in range(len(rect) // 2):
                rect[coor_index * 2] = int(rect[coor_index * 2] * resize_multiple)  # x值整体缩放
                rect[coor_index * 2 + 1] = int(rect[coor_index * 2 + 1] * resize_multiple)  # y值整体缩放
                # rect[coor_index * 2] += w_pos  # 偏移操作
                # rect[coor_index * 2 + 1] += h_pos
                rect[coor_index * 2] = max(min(rect[coor_index * 2], bg_width), 0)
                rect[coor_index * 2 + 1] = max(min(rect[coor_index * 2 + 1], bg_height), 0)
            # print("rect {] ; h_pos {} ; w_pos {} ".format(rect, h_pos, w_pos))
            # background[rect[1]: rect[-1], rect[0]:rect[2]] = image[rect[1] - h_pos: rect[-1] - h_pos,
            #                                                  rect[0] - w_pos: rect[2] - w_pos]
            background[rect[1]: rect[-1], rect[0]:rect[2]] = image[rect[1]: rect[-1], rect[0]: rect[2]]
            new_rect = [rect[0], rect[1], rect[2], rect[-1]]  # xmin, ymin, xmax, ymax，目的是为了方便更新xml文件
            box = (cls_type, new_rect)
            new_boxes.append(box)

        if filename.startswith('imgaug_'):
            filename = filename.split("_")[-1]
        new_filename = 'imgaug_%s_%s_' % (method_num + 1, epoch) + filename  # 更新背景后的图片名称
        cv2.imwrite(img_path + os.sep + new_filename + ext, background)
        change_Anno(xml_path + os.sep + filename + '.xml', xml_path + os.sep + new_filename + '.xml', new_boxes)


def label_split(top_dir, train_percent=0.9):
    def create_label(lines, label_type='train'):
        with open(top_dir + os.sep + '%s.txt' % label_type, 'w') as f:
            f.writelines(lines)

    with open(top_dir + os.sep + "trainval.txt") as f:
        lines = f.readlines()
    np.random.shuffle(lines)
    train_num = int(len(lines) * train_percent)
    trainlines = lines[:train_num]
    testlines = lines[train_num:]
    create_label(trainlines, label_type='trainval')
    create_label(testlines, label_type='test')


if __name__ == '__main__':
    print("start bg_change")
    top_dir = "./data/test_data"
    image_dir = top_dir + os.sep + 'JPEGImages'
    label_dir = top_dir + os.sep + 'Annotations'
    reset_dir(image_dir)
    reset_dir(label_dir)
    # bg_dir = "./data/bg_imgs"
    # imgfiles_l = os.listdir(image_dir)
    # bg_treat(image_dir, label_dir, imgfiles_l, bg_dir)

