# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-06-02 20:25:11
:LastEditTime: 2020-06-03 19:41:14
:LastEditors: ChenXiaolei
:Description: QR Code Helper  
:Description: Doc:https://github.com/lincolnloop/python-qrcode#advanced-usage
"""

import io
import qrcode


class QRCodeHelper(object):
    """
    :Description: 二维码帮助类
    """
    @classmethod
    def create_qr_code(self, data, version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4, fill_color="green", back_color="white"):
        """
        :Description: 
        :param data: 二维码数据
        :param version: 二维码的格子矩阵大小，可以是1到40，1最小为21*21，40是177*177
        :param error_correction: 二维码错误容许率，默认ERROR_CORRECT_M，容许小于15%的错误率
        :param box_size: 二维码每个小格子包含的像素数量
        :param border: 二维码到图片边框的小格子数，默认值为4
        :param fill_color: 填充颜色 默认绿色
        :param back_color: 背景颜色 默认白色
        :return: 图片流
        :last_editors: HuangJingCan
        """
        # 实例化二维码生成类
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
        )
        # 设置二维码数据
        qr.add_data(data=data)

        # 启用二维码颜色设置
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # 显示二维码
        # img.show()

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        return img, img_bytes
