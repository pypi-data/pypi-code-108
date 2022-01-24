import json
from PIL import Image, ImageFont, ImageDraw
import cv2, os
import numpy as np
import mmcv


def draw_box(num, data_root, results):
    for t in range(1, num + 1):
        with open(os.path.join(results, "results.json"), encoding='utf-8') as f:
            line = f.readline()
            d = json.loads(line)
            # print("d === ", d)
            index = t - 1
            name = d[index]['img_name']
            points = d[index]['points']
            texts = d[index]['texts']
            print("name == ", name)
            # print("points === ", points[0][0][0])
            # print("points === ", len(points))
            # print(name, points, texts)

            image = cv2.imread(os.path.join(data_root, "rename", name))
            for i in range(0, len(points)):
                x1 = int(points[i][0][0])
                x2 = int(points[i][0][1])
                x3 = int(points[i][1][0])
                x4 = int(points[i][1][1])
                x5 = int(points[i][2][0])
                x6 = int(points[i][2][1])
                x7 = int(points[i][3][0])
                x8 = int(points[i][3][1])
                color = (0, 0, 255)

                cv2.line(image, (x1, x2), (x3, x4), color, 2)
                cv2.line(image, (x3, x4), (x5, x6), color, 2)
                cv2.line(image, (x5, x6), (x7, x8), color, 2)
                cv2.line(image, (x7, x8), (x1, x2), color, 2)
            cv2img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pilimg = Image.fromarray(cv2img)
            draw = ImageDraw.Draw(pilimg)
            font = ImageFont.truetype(os.path.join(results, "simsun.ttf"), 22, encoding="utf-8")
            # cv2.putText(image, texts[i], (x1, x2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 0, 0))
            for i in range(0, len(points)):
                x1 = int(points[i][0][0])
                x2 = int(points[i][0][1])
                x3 = int(points[i][1][0])
                x4 = int(points[i][1][1])
                x5 = int(points[i][2][0])
                x6 = int(points[i][2][1])
                x7 = int(points[i][3][0])
                x8 = int(points[i][3][1])
                min_x = min(x1, x3, x5, x7)
                if min_x == x1:
                    min_y = x2
                if min_x == x3:
                    min_y = x4
                if min_x == x5:
                    min_y = x6
                if min_x == x7:
                    min_y = x8
                draw.text([min_x, min_y], texts[i], (255, 0, 0), font=font)
            cv2charimg = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)
            # cv2.imwrite(os.path.join('D:/Experiment/Text_Recognition/AE_TextSpotter/results/results_img/frame{}.jpg'.format(t)),cv2charimg)
            cv2.imwrite(os.path.join(results, "vis", name), cv2charimg)
            f.close()


def rename(data_root):
    num = 1
    if not os.path.exists(os.path.join(data_root, "rename")):
        os.mkdir(os.path.join(data_root, "rename"))
    test = data_root + "/test"
    for f in os.listdir(test):
        file = os.path.join(test, f)
        if os.path.isdir(file):
            continue
        print(file)
        f_exist = os.path.exists(file)
        if f_exist:
            image = cv2.imread(file)
            rename_file = os.path.join(data_root, "rename", "test_ReCTS_task3_and_task_4_{:06d}.jpg".format(num))
            print(rename_file)
            cv2.imwrite(rename_file, image)
            num = num + 1
    return num - 1


def prepare(data_root):
    cache_path = os.join(data_root, 'tda_rects_test_cache_file.json')
    test_img_root = os.join(data_root, 'rename/')
    img_names = [img_name for img_name in mmcv.utils.scandir(test_img_root, '.jpg')]

    img_infos = []
    print('Loading images...')
    for i, img_name in enumerate(img_names):
        if i % 1 == 0:
            print('%d / %d' % (i + 1, len(img_names)))
        img_path = test_img_root + img_name
        ann_file = None

        try:
            h, w, _ = mmcv.imread(img_path).shape
            img_info = dict(
                filename=img_name,
                height=h,
                width=w,
                annfile=ann_file)
            img_infos.append(img_info)
        except:
            print('Load image error when generating img_infos: %s' % img_path)

    with open(cache_path, 'w') as f:
        mmcv.dump(img_infos, f, file_format='json', ensure_ascii=False)
