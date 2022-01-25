#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   image_tool.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021-12-10 11:45     douly      1.0         image_tool
"""
# import lib
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def draw_chinese(_image, text, positive, font_size=20, font_color=(0, 0, 0, 255)):
	"""
	在图像上

	:param _image:
	:param text:
	:param positive:
	:param font_size:
	:param font_color:
	:return:
	"""
	cv2img = cv2.cvtColor(_image, cv2.COLOR_BGR2RGBA)  # cv2和PIL中颜色的hex码的储存顺序不同
	pilimg = Image.fromarray(cv2img)
	# PIL图片上打印汉字
	draw = ImageDraw.Draw(pilimg)  # 图片上打印
	font = ImageFont.truetype("SIMLI.TTF", font_size, encoding="utf-8")  # 参数1：字体文件路径，参数2：字体大小
	draw.text(positive, text, font_color, font=font)  # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体格式
	char_img = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGRA)  # PIL图片转cv2 图片

	return char_img


def fill_ceil(src, threshold=0):
	"""
	一种填充灰度图像孔洞的方法, 值threshold的点 则取附近3*3网格内,6个最大数的平均值,可以扩展添加算子和

	:param src:
	:param threshold:
	:return:
	"""
	for _r in range(2, src.shape[0] - 2):
		for _c in range(2, src.shape[1] - 2):
			if src[_r, _c] > threshold:
				continue
			else:
				_arr = src[_r - 1: _r + 1, _c - 1:_c + 1]
				_arr = _arr.flatten()
				# _arr.sort(reverse=True)
				_arr = -np.sort(-_arr)
				src[_r, _c] = np.average(_arr[:6])

	return src


def channel_3_4(src):
	(rols, cols) = src.shape[:2]
	dst = np.zeros((rols, cols, 4), dtype=np.uint8)
	for r in range(src.shape[0]):
		for c in range(src.shape[1]):
			_val = list(src[r, c])
			_val.append(255)
			dst[r, c] = _val
	return dst


def img_float32(img):
	return img.copy() if img.dtype != 'uint8' else (img / 255.).astype('float32')


def over(fore_ground, background):
	fore_ground, background = img_float32(fore_ground), img_float32(background)
	(fb, fg, fr, fa), (bb, bg, br, ba) = cv2.split(fore_ground), cv2.split(background)
	color_fg, color_bg = cv2.merge((fb, fg, fr)), cv2.merge((bb, bg, br))
	alpha_fg, alpha_bg = np.expand_dims(fa, axis=-1), np.expand_dims(ba, axis=-1)

	color_fg[fa == 0] = [0, 0, 0]
	color_bg[ba == 0] = [0, 0, 0]

	a = fa + ba * (1 - fa)
	a[a == 0] = np.NaN
	color_over = (color_fg * alpha_fg + color_bg * alpha_bg * (1 - alpha_fg)) / np.expand_dims(a, axis=-1)
	color_over = np.clip(color_over, 0, 1)
	color_over[a == 0] = [0, 0, 0]

	result_float32 = np.append(color_over, np.expand_dims(a, axis=-1), axis=-1)
	return (result_float32 * 255).astype('uint8')


def overlay_with_transparency(background, fore_ground, xmin=0, ymin=0, trans_percent=1):
	"""
	将前景透明图像叠加到后景图像上

	:param background: a 4 channel image, use as background
	:param fore_ground: a 4 channel image, use as foreground
	:param xmin: a coordinate in background. from where the fore_ground will be put
	:param ymin: a coordinate in background. from where the fore_ground will be put
	:param trans_percent: transparency of fore_ground. [0.0,1.0]
	:return: a merged image
	"""
	# we assume all the input image has 4 channels
	assert (background.shape[-1] == 4 and fore_ground.shape[-1] == 4)
	fore_ground = fore_ground.copy()
	roi = background[ymin:ymin + fore_ground.shape[0], xmin:xmin + fore_ground.shape[1]].copy()

	# opencv 通道拆分
	b, g, r, a = cv2.split(fore_ground)

	# opencv 通道合并
	fore_ground = cv2.merge((b, g, r, (a * trans_percent).astype(fore_ground.dtype)))

	roi_over = over(fore_ground, roi)
	# 注意用的都是copy,不会影响到原图
	result = background.copy()
	result[ymin:ymin + fore_ground.shape[0], xmin:xmin + fore_ground.shape[1]] = roi_over
	return result


def merge_image_by_image(left_image, right_image):
	"""
	将两张图片并列放置并且合并, 左右

	:param left_image:
	:param right_image:
	:return:
	"""
	(lrows, lcols, lchannels) = left_image.shape
	(rrows, rcols, rchannels) = right_image.shape
	assert lrows == rrows and lcols == rcols and lchannels == rchannels
	dst_image = np.zeros((lrows, lcols * 2, lchannels))
	dst_image[0:lrows, 0:lcols] = left_image
	dst_image[0: lrows, lcols:2 * lcols] = right_image
	return dst_image.copy()
