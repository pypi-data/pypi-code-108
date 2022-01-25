import os, sys, threading, math, time, yaml
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
from imgaug import augmenters as iaa
import imgaug as ia
from tqdm import tqdm
from datatools.aug.bg_changed import bg_treat
from loguru import logger
# import argparse


def get_methods_from_yml(aug_file):
    f = open(aug_file, encoding='utf8')
    data_dict = yaml.load(f, Loader=yaml.Loader)
    methods = []
    if 'Sequential' in data_dict.keys():
        seq_methods = []
        for method, paras in data_dict['Sequential'].items():
            if method == 'bg_changed':
                methods.append({method: paras})

            elif method == 'WithColorspace':
                k = data_dict["Sequential"][method]
                if 'children' in k.keys():
                    if type(k['children']) == dict:
                        tmp1 = k['children']
                        for tmp2_method, tmp2_value in tmp1.items():
                            if type(tmp1[tmp2_method]) == dict:
                                if 'children' in tmp1[tmp2_method].keys():
                                    tmp3 = tmp1[tmp2_method]['children']
                                    for tmp3_method, tmp3_value in tmp3.items():
                                        tmp2_value = getattr(iaa, tmp3_method)(tmp3_value)
                                tmp1[tmp2_method]['children'] = tmp2_value
                        k['children'] = getattr(iaa, tmp2_method)(**tmp1[tmp2_method])
                seq_methods.append(getattr(iaa, 'WithColorspace')(**k))
            elif method == 'Resize':
                seq_methods.append(getattr(iaa, method)(paras))
            else:
                if paras == None:
                    seq_methods.append(getattr(iaa, method)())
                elif type(paras) in [int, float, list]:
                    seq_methods.append(getattr(iaa, method)(paras))
                elif type(paras) == dict:
                    paras = {key: eval(value) if type(value) == str else value for key, value in paras.items()}
                    seq_methods.append(getattr(iaa, method)(**paras))
        methods.append(iaa.Sequential(seq_methods))
    else:
        for method, paras in data_dict.items():
            if method == 'bg_changed':
                methods.append({method: paras})
            elif method == 'WithColorspace':
                k = data_dict[method]
                if 'children' in k.keys():
                    if type(k['children']) == dict:
                        tmp1 = k['children']
                        for tmp2_method, tmp2_value in tmp1.items():
                            if type(tmp1[tmp2_method]) == dict:
                                if 'children' in tmp1[tmp2_method].keys():
                                    tmp3 = tmp1[tmp2_method]['children']
                                    for tmp3_method, tmp3_value in tmp3.items():
                                        tmp2_value = getattr(iaa, tmp3_method)(tmp3_value)
                                tmp1[tmp2_method]['children'] = tmp2_value
                        k['children'] = getattr(iaa, tmp2_method)(**tmp1[tmp2_method])
                methods.append(getattr(iaa, 'WithColorspace')(**k))
            elif method == 'Resize':
                methods.append(getattr(iaa, method)(paras))
            elif method == "basic":  # 基础配置非增强方法配置
                continue
            else:
                if paras == None:
                    methods.append(getattr(iaa, method)())
                elif type(paras) in [int, float, list]:
                    methods.append(getattr(iaa, method)(paras))
                elif type(paras) == dict:
                    paras = {key: eval(value) if type(value) == str else value for key, value in paras.items()}
                    methods.append(getattr(iaa, method)(**paras))
    return data_dict, methods


def read_xml_annotation(xml_dir, image_id):
    in_file = open(os.path.join(xml_dir, image_id), encoding='utf8')
    tree = ET.parse(in_file)
    xmlroot = tree.getroot()
    if xmlroot.find('object') is None:  # 如标签文件没有目标物体，则不予增强
        return None
    bndboxlist = []
    for object in xmlroot.findall('object'):  # 找到root节点下的所有country节点
        bndbox = object.find('bndbox')  # 子节点下节点rank的值
        xmin = int(bndbox.find('xmin').text)
        xmax = int(bndbox.find('xmax').text)
        ymin = int(bndbox.find('ymin').text)
        ymax = int(bndbox.find('ymax').text)
        bndboxlist.append([xmin, ymin, xmax, ymax])
    bndbox = xmlroot.find('object').find('bndbox')
    return bndboxlist  # 以多维数组的形式保存


def change_xml_list_annotation(xml_dir, image_id, new_target, method_num, epoch):
    in_file = open(os.path.join(xml_dir, image_id + '.xml'))  # 读取原来的xml文件
    tree = ET.parse(in_file)  # 读取xml文件
    xmlroot = tree.getroot()
    size = xmlroot.find("size")
    width = int(size.find("width").text)
    height = int(size.find("height").text)
    index = 0
    # 将bbox中原来的坐标值换成新生成的坐标值
    for object in xmlroot.findall('object'):  # 找到root节点下的所有country节点
        bndbox = object.find('bndbox')  # 子节点下节点rank的值
        new_xmin = new_target[index][0]
        new_ymin = new_target[index][1]
        new_xmax = new_target[index][2]
        new_ymax = new_target[index][3]

        xmin = bndbox.find('xmin')
        xmin.text = str(max(new_xmin, 0))
        ymin = bndbox.find('ymin')
        ymin.text = str(max(new_ymin, 0))
        xmax = bndbox.find('xmax')
        xmax.text = str(min(new_xmax, width))
        ymax = bndbox.find('ymax')
        ymax.text = str(min(new_ymax, height))
        index = index + 1
    tree.write(os.path.join(xml_dir, "imgaug_%s_%s_" % (method_num + 1, epoch) + str(image_id) + '.xml'))


def aug_act(args, XML_DIR, IMG_DIR, imgfiles, methods):

    if args["basic"]["random"]:
        print('进入随机增强模式')
        aug_methods = [np.random.choice(methods)]  # 每个xml文件随机选择一种的增强方法
    else:
        print('进入常规增强模式')
        aug_methods = methods  # 每种所列方法，均进行一次增强操作
    flag_Sequential_bg_changed = False
    for method_num, aug_method in enumerate(aug_methods):
        for epoch in range(1, args["basic"]["aug_times"] + 1):
            logger.info("aug using the {} method {} round".format(method_num+1, epoch))

            # bg_changed 方法特殊处理，imgaug 不包括该方法，因此需单独处理
            # 增强方法分别处理并分别生成新图片时，该方法先执行
            if type(aug_method) == dict and aug_method.get("bg_changed", None) and not args.get("Sequential", None):
                bg_treat(IMG_DIR, XML_DIR, imgfiles, aug_method["bg_changed"]["bg_path"], method_num, epoch)
            elif type(aug_method) == dict and aug_method.get("bg_changed", None) and args.get("Sequential", None):
                flag_Sequential_bg_changed = True
                continue
            else:
                for imgfile in tqdm(imgfiles):
                    image_id = os.path.splitext(imgfile)[0]
                    bndbox = read_xml_annotation(XML_DIR, image_id + '.xml')
                    if bndbox:
                        new_bndbox_list = []
                        seq_det = aug_method.to_deterministic()  # 保持坐标和图像同步改变，而不是随机
                        img = Image.open(os.path.join(IMG_DIR, imgfile))  # 读取图片
                        img = img.convert('RGB')
                        img = np.array(img)
                        for i in range(len(bndbox)):  # bndbox坐标增强，依次处理所有的bbox
                            bbs = ia.BoundingBoxesOnImage(
                                [ia.BoundingBox(x1=bndbox[i][0], y1=bndbox[i][1], x2=bndbox[i][2], y2=bndbox[i][3])],
                                shape=img.shape)
                            bbs_aug = seq_det.augment_bounding_boxes([bbs])[0]
                            new_bndbox_list.append([int(bbs_aug.bounding_boxes[0].x1),
                                                    int(bbs_aug.bounding_boxes[0].y1),
                                                    int(bbs_aug.bounding_boxes[0].x2),
                                                    int(bbs_aug.bounding_boxes[0].y2)])
                        image_aug = seq_det.augment_images([img])[0]
                        new_img_name = 'imgaug_%s_%s_' % (method_num + 1, epoch) + imgfile
                        path = os.path.join(IMG_DIR, new_img_name)  # 存储变化后的图片
                        Image.fromarray(image_aug).save(path)
                        change_xml_list_annotation(XML_DIR, image_id, new_bndbox_list, method_num, epoch)  # 存储变化后的XML

                        # 增强方法先后处理并生成新图片时，该方法最后执行
                        if flag_Sequential_bg_changed:
                            imgfiles_Sequential = [new_img_name]
                            for epoch in range(1, args["basic"]["aug_times"] + 1):
                                bg_treat(IMG_DIR, XML_DIR, imgfiles_Sequential, args["Sequential"]["bg_changed"]["bg_path"], method_num, epoch)


def threading_treat(args, XML_DIR, IMG_DIR, imgfiles, methods):  # 使用多线程处理，以提升速度
    threads = args["basic"]["thread_num"]
    if type(threads) == bool:
        threads = os.cpu_count()
    elif type(threads) == int and threads > 0:
        threads = threads
    else:
        raise TypeError("thread_num should be bool or positive int not {}".format(args["basic"]["thread_num"]))

    print('nums of %s threading are running...' % threads)
    NUMS = len(imgfiles)
    num_part = math.ceil(NUMS / threads)  # 计算每个线程要处理的最大数据量
    temp_t = []
    for thread_num in range(threads):
        son_imgfiles = imgfiles[num_part * thread_num: num_part * (thread_num + 1)]
        t = threading.Thread(target=aug_act, args=(args, XML_DIR, IMG_DIR, son_imgfiles, methods))
        temp_t.append(t)
        t.start()
    for t in temp_t:
        t.join()


def reset_dir(filepath):
    for each_file in os.listdir(filepath):
        if each_file.startswith('imgaug_'):
            os.remove(filepath + os.sep + each_file)


def label_create_split(args, data_dir):
    """
    valid_data would be splited from original, not include the augment data.
    """

    def create_label(lines, label_type='train'):
        with open(data_dir + os.sep + 'ImageSets/Main/%s.txt' % label_type, 'w', encoding='utf8') as f:
            f.writelines(lines)

    os.makedirs(data_dir + os.sep + 'ImageSets/Main', exist_ok=True)
    lines = []
    for labelfile in os.listdir(data_dir + os.sep + 'Annotations'):
        filename = os.path.splitext(labelfile)[0]
        lines.append(filename + "\n")
    orilines = [i for i in lines if not i.startswith('imgaug_')]
    np.random.shuffle(orilines)
    val_num = int(len(orilines) * args["basic"]["val_percent"])
    testlines = orilines[: val_num]
    trainlines = [i for i in lines if i not in testlines]
    np.random.shuffle(trainlines)
    create_label(trainlines, label_type='trainval')
    create_label(testlines, label_type='test')
    print('data split complete')


# def data_aug(aug_file, data_dir):
#     """
#     数据集新切分，后增强
#     只对 trainval.txt 部分增强
#     Args:
#         aug_file:
#         data_dir:
#
#     Returns:
#
#     """
#     config_dict, methods = get_methods_from_yml(aug_file)
#
#     t1 = time.time()
#     if not os.path.exists(data_dir):
#         raise FileNotFoundError('未能找到相应文件夹，请核查传入的路径')
#     IMG_DIR = data_dir + os.sep + "JPEGImages"
#     XML_DIR = data_dir + os.sep + "Annotations"
#     reset_dir(IMG_DIR)
#     reset_dir(XML_DIR)
#
#     imgfiles = os.listdir(IMG_DIR)
#     if not config_dict["basic"]["thread_num"]:
#         aug_act(config_dict, XML_DIR, IMG_DIR, imgfiles, methods)  # 未采用多线程
#     else:
#         threading_treat(config_dict, XML_DIR, IMG_DIR, imgfiles, methods)
#     if config_dict["basic"]["split"]:
#         label_create_split(config_dict, data_dir)
#
#     # 生成新的trainval.txt
#     voc_txt_dir = os.path.join(data_dir, "ImageSets", "Main")
#     if os.path.exists(voc_txt_dir):
#         for voc_txt in os.listdir(voc_txt_dir):
#             rm_path = os.path.join(voc_txt_dir, voc_txt)
#             if os.path.isfile(rm_path):
#                 os.remove(rm_path)
#     else:
#         os.makedirs(voc_txt_dir, exist_ok=True)
#     txt_path = os.path.join(voc_txt_dir, "trainval.txt")
#     xml_names = []
#     for root, _, files in os.walk(XML_DIR):
#         for xml_file in files:
#             xml_name = os.path.splitext(xml_file)[0]
#             xml_names.append(xml_name)
#     with open(txt_path, "w", encoding="utf-8") as fw:
#         for item in xml_names:
#             item = item.replace("\n", "").replace("\r\n", "")
#             fw.write(item)
#             fw.write("\n")
#
#     print('time cost : %sS' % round(time.time() - t1, 2))


def data_aug(aug_file, data_dir):
    """
    数据集新切分，后增强
    切分后，Main 文件中必含有 trainval.txt
    只对 trainval.txt 部分增强
    Args:
        aug_file:
        data_dir:

    Returns:

    """
    config_dict, methods = get_methods_from_yml(aug_file)

    t1 = time.time()
    if not os.path.exists(data_dir):
        raise FileNotFoundError('未能找到相应文件夹，请核查传入的路径')
    IMG_DIR = data_dir + os.sep + "JPEGImages"
    XML_DIR = data_dir + os.sep + "Annotations"
    reset_dir(IMG_DIR)
    reset_dir(XML_DIR)

    voc_txt_dir = os.path.join(data_dir, "ImageSets", "Main")
    trainval_txt_path = os.path.join(voc_txt_dir, "trainval.txt")
    test_txt_path = os.path.join(voc_txt_dir, "test.txt")

    # rest trainval.txt
    with open(trainval_txt_path, "r", encoding="utf-8") as fr:
        xml_trainval_reset = fr.readlines()
    with open(trainval_txt_path, "w", encoding="utf-8") as fw:
        for item in xml_trainval_reset:
            if not item.strip().startswith("imgaug_"):
                item = item.replace("\n", "").replace("\r\n", "")
                fw.write(item)
                fw.write("\n")

    # 读取原始 trainval.txt
    with open(trainval_txt_path, "r", encoding="utf-8") as fr:
        xml_trainval_ori = fr.readlines()
        xml_trainval_ori = [item.strip() for item in xml_trainval_ori]
    with open(test_txt_path, "r", encoding="utf-8") as fr:
        xml_test_ori = fr.readlines()
        xml_test_ori = [item.strip() for item in xml_test_ori]

    # 只有 trainval.txt 中的图片参与增强
    imgfiles_all = os.listdir(IMG_DIR)
    imgfiles = []
    for item in imgfiles_all:
        if item.split(".")[0] in xml_trainval_ori:
            imgfiles.append(item)

    if not config_dict["basic"]["thread_num"]:
        aug_act(config_dict, XML_DIR, IMG_DIR, imgfiles, methods)  # 未采用多线程
    else:
        threading_treat(config_dict, XML_DIR, IMG_DIR, imgfiles, methods)
    # if config_dict["basic"]["split"]:
    #     label_create_split(config_dict, data_dir)

    # 生成新的trainval.txt
    xml_names = []
    for root, _, files in os.walk(XML_DIR):
        for xml_file in files:
            xml_name = os.path.splitext(xml_file)[0]
            xml_names.append(xml_name)
    with open(trainval_txt_path, "a+", encoding="utf-8") as fw:
        for item in xml_names:
            if item.startswith("imgaug_"):
                item = item.replace("\n", "").replace("\r\n", "")
                fw.write(item)
                fw.write("\n")

    print('time cost : %sS' % round(time.time() - t1, 2))


if __name__ == "__main__":
    # top_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # args = get_args()
    # aug(args)

    aug_config = "./aug.yml"
    data_folder = "../../test/voc_eva_clothes_helmet"
    data_aug(aug_config, data_folder)

    # IMG_DIR = data_folder + os.sep + "JPEGImages"
    # XML_DIR = data_folder + os.sep + "Annotations"
    # reset_dir(IMG_DIR)
    # reset_dir(XML_DIR)
