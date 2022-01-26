#!/usr/bin/env python3.7
# encoding: utf-8
# 获取验证码

from selenium import webdriver
from PIL import Image, ImageEnhance
import pytesseract
import HTest


def verification(driver, path, point):
    """
    验证码图片处理，返回验证码数字
    获取验证码图片的长宽（120,35），获取验证码x,y轴坐标（1250, 320），从point.py中获得
    :param driver:
    :param path: 截图存放的路径, 例如 path = "../content/screenshots/"
    :param point: 验证码的坐标或者我们需要截取的位置坐标，例如 point = (1250, 320, 1370, 355)
    :return: 返回验证码数字
    order by taolei
    """
    driver.save_screenshot(path + "01.png")
    driver.maximize_window()
    i = Image.open(path + "01.png")
    i.crop(point).save(path + "02.png")  # 保存验证码图片
    # 获取验证码图片，读取验证码
    imageCode = Image.open(path + "02.png")  # 图像增强，二值化
    imageCode.load()
    sharp_img = ImageEnhance.Contrast(imageCode).enhance(2.0)
    sharp_img.save(path + "03.png")
    sharp_img.load()  # 对比度增强
    code = pytesseract.image_to_string(sharp_img).strip()
    return code
