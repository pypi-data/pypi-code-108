"""
用cv2处理
"""
import ast
import base64
import io

import PIL
import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
import requests
from PIL import Image
from cv2 import cv2
from collections import Counter

class ImageProcessor:
    def __init__(self):
        self.pharmcube_ocr_url = 'http://localhost/2txt'
        # self.pharmcube_ocr_url ='http://101.201.249.176:1990/2txt'
        # self.pharmcube_ocr_url = 'http://localhost/2txt_CV'
        self.baidu_ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
        self.request_url, self.headers = None,None

    def get_baidu_ocr_config(self):
        # 获取access_token , client_id 为官网获取的AK， client_secret 为官网获取的SK
        appid = "25533636"
        client_id = "PLvUz16ePip4txCcYXk2Ablh"
        client_secret = "8HXb8DIo2t7eNaw1aD6XGZi4U1Kytj41"
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        host = f"{token_url}?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
        response = requests.get(host)
        access_token = response.json().get("access_token")

        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_url = f"{request_url}?access_token={access_token}"
        return request_url, headers

    @staticmethod
    def read_image(image: str, method='cv2'):
        # opencv 读取图片数据格式为numpy.ndarray，(高、宽、通道)
        # PIL用PIL.Image.Image   (宽、高、通道), Image对象有crop功能，也就是图像切割功能
        if method == 'PIL':
            # PIL.PngImagePlugin.PngImageFile，PIL读取顺序RGB 并通过.convert来定义读取图片类型：1:位图  L：灰度图  RGB:彩色图
            image = Image.open(image)
        elif method == 'cv2':
            image = cv2.imread(image, flags=1)  # ndarray，opencv读取顺序BGR, flag=1默认彩色图片， 0：读取灰度图
        else:
            image = mpimg.imread(image)  # ndarray, 二维grb ，3个通道
        return image

    @staticmethod
    def show_image(img, other_mode=False):
        # rgb 格式显示图像,cv2.imshow() BGR模式显示,img.show()  PIL对象自带,RGB模式, plt.imshow()  RGB
        if isinstance(img, str):  # 图像路径
            img = ImageProcessor.read_image(img, method='cv2')  # ndarray
        try:
            if other_mode:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR转RGB
        finally:
            plt.imshow(img)
            plt.xticks([]), plt.yticks([])
            plt.show()

    def format_image(self, image, format='Image'):
        if format == 'Image':
            if isinstance(image, str):
                image = Image.open(image)
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(image)  # -np数组转化为img对象
        else:
            if isinstance(image, str):
                image = cv2.imread(image, 1)
            elif isinstance(image, PIL.PpmImagePlugin.PpmImageFile) | isinstance(image, PIL.Image.Image):
                image = np.array(image)  # img对象转化为np数组
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def save_image(self):
        # PIL.Image.save()保存RGB图像
        # cv2.imwrite()--opencv---保存图片，等效BGR2RGB
        pass

    def get_text_from_one_image(self, image, method='pharmcube_ocr'):
        """
        使用ocr提取图像中的文本
        Args:
            image: 图像-路径/Image/ndarray
            method: pharmcube_ocr/baidu_ocr/pytesseract

        Returns:

        """
        image = self.format_image(image, 'Image')  # imgae-RGB-IMGAGE对象
        if image.mode != 'GBA':
            image = image.convert('RGB')
        if method == 'pharmcube_ocr':
            buf = io.BytesIO()
            image.save(buf, format='JPEG')
            byte_im = buf.getvalue()
            response = requests.post(self.pharmcube_ocr_url, files={'file': byte_im})
            text = ast.literal_eval(response.text)
            text = '\n'.join(text)
        elif method == 'baidu_ocr':  # 付费
            image = np.array(image)
            image = cv2.imencode('.jpg', image)[1]
            image = image.tobytes()
            image = base64.b64encode(image).decode('utf8')
            body = {
                "image": image,
                "language_type": "auto_detect",
                "recognize_granularity": "small",
                "detect_direction": "true",
                "vertexes_location": "true",
                "paragraph": "true",
                "probability": "true",
            }
            if not self.request_url:
                self.request_url, self.headers, = self.get_baidu_ocr_config()
            response = requests.post(self.request_url, headers=self.headers, data=body)
            content = response.content.decode("UTF-8")
            content = eval(content)
            text = ''
            if 'words_result' in content.keys():
                content= content['words_result']
                for c in content:
                    text += (c['words'].replace(' ', '') + '\n')
        else:  # pytesseract
            text = pytesseract.image_to_string(image, lang="chi_sim")  # png
            text = text.replace(' ', '')
        return text

    def get_tables_from_image(self, image, ocr_method=None):
        """
        从图像中获取若干表格的位置以及表格内容
        Args:
            image:
            ocr_method: 使用ocr识别单元格文本

        Returns:

        """
        image = self.format_image(image, 'cv2')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert raw to gray picture and binary
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)

        # get horizontal and vertical line
        rows, cols = binary.shape
        scale = 40
        # 识别横线:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_col = cv2.dilate(eroded, kernel, iterations=1)

        # 识别竖线
        scale = 40  # can use different threshold
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_row = cv2.dilate(eroded, kernel, iterations=1)

        mat_mask = dilated_col + dilated_row  # 表格的线（横线+竖线）
        bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)  # 交点
        ys, xs = np.where(bitwise_and > 0)

        # '''get the start coordinate of each line'''
        # lines_pos = np.where(dilated_col > 0)
        # linepos = Counter(lines_pos[0])
        # start = 0
        # starts = []
        # for i in linepos:
        #     num = linepos[i]
        #     tmp = lines_pos[1][start:start + num][0]
        #     start += num
        #     starts.append(tmp)
        # start_pos = min(starts)
        #
        # '''mark left margin if it do not been recognized'''
        # linecols = Counter(ys)
        # st = 0
        # for i in linecols:
        #     ys = np.insert(ys, st, i)
        #     xs = np.insert(xs, st, start_pos)
        #     st += linecols[i]
        #     st += 1


        contours, hierarchy = cv2.findContours(mat_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        tables_location = []
        tables = []
        for c in contours:
            if c.size > 4:
                if cv2.contourArea(c) > image.shape[1]:
                    left = np.min(c, axis=0)[0][0]
                    top = np.min(c, axis=0)[0][1]
                    right = np.max(c, axis=0)[0][0]
                    bottom = np.max(c, axis=0)[0][1]

                    tmp_xs = []
                    tmp_ys = []
                    for x, y in zip(xs, ys):
                        if ((left - 10) < x < (right + 10)) and ((top - 10) < y < (bottom + 10)):
                            tmp_xs.append(x)
                            tmp_ys.append(y)  # 顺序，点是从左到右一次排
                    if (not tmp_ys) | (not tmp_xs):
                        continue
                    tmp_xs = self._format_coordinates(tmp_xs)
                    tmp_ys = self._format_coordinates(tmp_ys)
                    table = self._get_table_from_coordinates(tmp_xs, tmp_ys)
                    tables_location.append((left, top, right, bottom))

                    if ocr_method:
                        tmp_table = []
                        for row in table:
                            t = []
                            for cell in row:
                                cell_image = gray[max(0,cell[1]-5):cell[3], cell[0]:cell[2]]
                                t.append(self.get_text_from_one_image(cell_image, ocr_method))
                            tmp_table.append(t)
                        tables.append(tmp_table)
                    else:
                        tables.append(table)

        # 在图像中表格从上往下排
        sorted_tables = []
        tmp_tables_location = {t[1]: e for e, t in enumerate(tables_location)}
        for t in sorted(tmp_tables_location.keys()):
            sorted_tables.append(tables[tmp_tables_location.get(t)])
        tables_location.sort(key=lambda x: x[1])
        return sorted_tables, tables_location

    def _format_coordinates(self, coordinates):
        # 对于一个表格，格式化表格坐标，【0，1，40，10，11，40】--》【0，0，10，10，40，40】
        sorted_coordinates = np.sort(coordinates)
        format_dict = {sorted_coordinates[0]: sorted_coordinates[0]}
        start_point = sorted_coordinates[0]

        for i in range(len(sorted_coordinates) - 1):
            if sorted_coordinates[i + 1] - sorted_coordinates[i] > 10:
                start_point = sorted_coordinates[i + 1]
            format_dict.update({sorted_coordinates[i + 1]: start_point})

        return [format_dict.get(c) for c in coordinates]  # 有重复

    def _get_table_from_coordinates(self, xs, ys):
        """
        # 对于一个表格，根据横向和纵向坐标，扣取其中的单元格坐标信息
        Args:
            xs: 横向坐标
            ys: 竖向坐标

        Returns:格式化的表格,列表，每个元素是一行（列表），每行中有若干(left, top, right, bottom)
            【[(left, top, right, bottom)]】
        """
        table_dict = dict()
        table = []
        column = None
        for x, y in zip(xs, ys):
            if y != column:
                table_dict[y] = {x}
                column = y
            else:
                table_dict[y].add(x)

        # 不存在一个字段名称在上，两个字段值对应在下的情况
        if len(table_dict) > 1:
            columns = sorted(list(table_dict.keys()))
            for c in range(len(columns) - 1):
                top = columns[c]
                bottom = columns[c + 1]
                all_xs = table_dict.get(top) & table_dict.get(bottom)
                all_xs = sorted(list(all_xs))
                t = []
                if len(all_xs) >= 2:
                    for x in range(len(all_xs) - 1):
                        left = all_xs[x]
                        right = all_xs[x + 1]
                        t.append((left, top, right, bottom))
                table.append(t)
        return table


if __name__ == '__main__':
    img = "/home/zyl/disk/PharmAI/pharm_ai/intel/data/test.PNG"
    i_p = ImageProcessor()
    t, t_l = i_p.get_tables_from_image(img,'pharmcube_ocr')
    print(t)
    print(t_l)

    # t, t_l = i_p.get_tables_from_image(img, 'baidu_ocr')
    # print(t)
    # print(t_l)
    #
    # t, t_l = i_p.get_tables_from_image(img, 'tr_ocr')
    # print(t)
    # print(t_l)
