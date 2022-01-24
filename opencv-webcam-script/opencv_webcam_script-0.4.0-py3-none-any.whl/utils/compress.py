# 压缩文件
# 创建人：曾逸夫
# 创建时间：2022-01-19

import zipfile
import tarfile
import sys
import os
from tqdm import tqdm
import time
from opencv_webcam.utils.time_format import time_format

ROOT_PATH = sys.path[0]  # 项目根目录
COMPRESS_SUFFIX = ['zip', 'tar']  # 压缩文件格式


# 判断压缩文件格式
def is_compressFile(compressStyle):
    if compressStyle not in COMPRESS_SUFFIX:
        print(f'{compressStyle}：不正确！程序退出！')
        sys.exit()


# webcam压缩
def webcam_compress(compressStyle, is_autoCompressName, compressName, preCompressFilePath, compressMode):
    if (is_autoCompressName):
        # 自动命名
        compressNameTmp = str(preCompressFilePath).split('/')[-1]  # 获取帧目录名称
        # 自动命名压缩文件名称
        compressName = f'{ROOT_PATH}/{compressNameTmp}.{compressStyle}'

    file_list = os.listdir(preCompressFilePath)  # 获取目录下的文件名称
    file_tqdm = tqdm(file_list)  # 获取进度条

    # ----------压缩开始----------
    compress_startTime = time.time()  # 压缩开始时间
    if (compressStyle == COMPRESS_SUFFIX[0]):
        # zip压缩
        compress_file = zipfile.ZipFile(compressName, compressMode)
        for i in file_tqdm:
            file_tqdm.set_description(f'正在压缩：{i}')
            compressing_file = f'{preCompressFilePath}/{i}'
            compress_file.write(
                compressing_file, compress_type=zipfile.ZIP_DEFLATED)  # 写入zip文件
    elif (compressStyle == COMPRESS_SUFFIX[1]):
        # tar压缩
        compress_file = tarfile.open(compressName, compressMode)
        for i in file_tqdm:
            file_tqdm.set_description(f'正在压缩：{i}')
            compressing_file = f'{preCompressFilePath}/{i}'
            compress_file.add(compressing_file)  # 写入tar文件

    # ----------压缩结束----------
    compress_file.close()
    compress_endTime = time.time()  # 压缩结束时间
    compress_totalTime = compress_endTime - compress_startTime
    print(f'文件压缩成功！用时：{time_format(compress_totalTime)}，已保存在：{compressName}')
