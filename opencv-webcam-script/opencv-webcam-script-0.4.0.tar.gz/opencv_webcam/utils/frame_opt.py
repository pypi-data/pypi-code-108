# 视频帧操作函数
# 创建人：曾逸夫
# 创建时间：2022-01-04

import cv2
import sys


# 帧保存
def frame_opt(frame,
              frame_savePath,
              frame_num,
              is_resizeFrame,
              resize_frame,
              resizeRatio_frame,
              frame_namePrefix,
              frame_saveStyle,
              jpg_quality,
              png_quality):

    # 判断图片质量范围
    if (jpg_quality < 0 or jpg_quality > 100):
        print(f'JPG质量系数超出范围！无法保存！')
        sys.exit()  # 结束程序

    if (png_quality < 0 or png_quality > 9):
        print(f'PNG质量系数超出范围！无法保存！')
        sys.exit()  # 结束程序

    if (is_resizeFrame):
        # 重塑视频帧尺寸
        w_resize = int(
            resize_frame[0] * resizeRatio_frame)  # 重塑宽度
        h_resize = int(
            resize_frame[1] * resizeRatio_frame)  # 重塑高度
        frame_new = cv2.resize(
            frame, (w_resize, h_resize), interpolation=cv2.INTER_AREA)  # 重塑

        if (frame_saveStyle == 'jpg'):
            cv2.imwrite(
                f'./{frame_savePath}/{frame_namePrefix}-{frame_num}.{frame_saveStyle}', frame_new,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
        elif (frame_saveStyle == 'png'):
            cv2.imwrite(
                f'./{frame_savePath}/{frame_namePrefix}-{frame_num}.{frame_saveStyle}', frame_new,
                [int(cv2.IMWRITE_PNG_COMPRESSION), png_quality])
        else:
            print(f'帧格式有问题！无法保存！')
            sys.exit()  # 结束程序

    else:
        if (frame_saveStyle == 'jpg'):
            cv2.imwrite(
                f'./{frame_savePath}/{frame_namePrefix}-{frame_num}.{frame_saveStyle}', frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
        elif (frame_saveStyle == 'png'):
            cv2.imwrite(
                f'./{frame_savePath}/{frame_namePrefix}-{frame_num}.{frame_saveStyle}', frame,
                [int(cv2.IMWRITE_PNG_COMPRESSION), png_quality])
        else:
            print(f'帧格式有问题！无法保存！')
            sys.exit()  # 结束程序
