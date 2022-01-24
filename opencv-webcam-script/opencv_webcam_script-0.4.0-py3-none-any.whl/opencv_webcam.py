# OpenCV Webcam Script v0.4
# 创建人：曾逸夫
# 创建时间：2022-01-17

import cv2
from pathlib import Path
import argparse
import time
import os
import sys
from opencv_webcam.utils.ows_path import increment_path
from opencv_webcam.utils.hotkey import hotkey_judge
from opencv_webcam.utils.frame_opt import frame_opt
from opencv_webcam.utils.log import is_logSuffix, log_management
from opencv_webcam.utils.args_yaml import argsYaml
from opencv_webcam.utils.compress import webcam_compress, is_compressFile
from opencv_webcam.utils.time_format import time_format


ROOT_PATH = sys.path[0]  # 项目根目录
OWS_VERSION = 'OpenCV Webcam Script v0.4'  # 版本号


def parse_args(known=False):
    parser = argparse.ArgumentParser(description='OpenCV Webcam Script v0.4')
    parser.add_argument('--device', '-dev', default='0',
                        type=str, help='device index for webcam, 0 or rtsp')
    parser.add_argument('--quit', '-q', default="q",
                        type=str, help='quit key for webcam')
    parser.add_argument('--is_autoSaveFrame', '-isasf',
                        action='store_true', help='is auto save frame')
    parser.add_argument('--is_handSaveFrame', '-ishsf',
                        action='store_true', help='is hand save frame')
    parser.add_argument('--is_resizeFrame', '-isrf',
                        action='store_true', help='is resize frame')
    parser.add_argument('--frame_saveDir', '-fsd',
                        default="./WebcamFrame", type=str, help='save frame dir')
    parser.add_argument('--frame_dirName', '-fdn',
                        default="frames", type=str, help='save frame dir name')
    parser.add_argument('--frame_nSave', '-fns', default=1,
                        type=int, help='n frames save a frame (auto save frame)')
    parser.add_argument('--frame_capKey', '-fck', default="a",
                        type=str, help='frame capture key (hand save frame)')
    parser.add_argument('--resize_frame', '-rf',
                        default=[640, 480], type=int, nargs='+', help='resize frame save')
    parser.add_argument('--resizeRatio_frame', '-rrf',
                        default=1.0, type=float, help='resize ratio frame save')
    parser.add_argument('--frame_namePrefix', '-fnp',
                        default="frame", type=str, help='frame name prefix')
    parser.add_argument('--frame_saveStyle', '-fss',
                        default="jpg", type=str, help='frame save style')
    parser.add_argument('--jpg_quality', '-jq',
                        default=95, type=int, help='frame save jpg quality (0-100) default 95')
    parser.add_argument('--png_quality', '-pq',
                        default=3, type=int, help='frame save jpg quality (0-9) default 3')
    parser.add_argument('--pause', '-p',
                        default="p", type=str, help='webcam pause')
    parser.add_argument('--auto_frameNum', '-afn',
                        default=0, type=int, help='auto save number of frames')

    # 日志
    parser.add_argument('--logName', '-ln',
                        default="test.log", type=str, help='log save name')
    parser.add_argument('--logMode', '-lm',
                        default="a", type=str, help='log write mode')
    # 压缩
    parser.add_argument('--is_compress', '-isc',
                        action='store_true', help='is compress file')
    parser.add_argument('--compressStyle', '-cs',
                        default="zip", type=str, help='compress style')
    parser.add_argument('--is_autoCompressName', '-isacn',
                        action='store_true', help='is auto compress name')
    parser.add_argument('--compressName', '-cn',
                        default="test", type=str, help='compress save name')
    parser.add_argument('--compressMode', '-cm',
                        default="w", type=str, help='compress save mode, tar w:gz')
    args = parser.parse_known_args()[0] if known else parser.parse_args()
    return args


# Webcam OpenCV
def webcam_opencv(device_index="0",
                  quit_key="q",
                  pause_key="p",
                  is_autoSaveFrame=False,
                  frame_saveDir="./WebcamFrame",
                  frame_dirName="frames",
                  frame_nSave=1,
                  auto_frameNum=0,
                  is_handSaveFrame=False,
                  frame_capKey="a",
                  is_resizeFrame=False,
                  resize_frame=[640, 480],
                  resizeRatio_frame=1.0,
                  frame_namePrefix="frame",
                  frame_saveStyle="jpg",
                  jpg_quality=95,
                  png_quality=3,
                  logName="test.log",
                  logMode="a",
                  is_compress=False,
                  compressStyle="zip",
                  is_autoCompressName=False,
                  compressName="test",
                  compressMode="w"):

    keyList = [quit_key, frame_capKey, pause_key]  # 快捷键列表
    hotkey_judge(keyList)  # 快捷键冲突判断

    # 日志文件
    is_logSuffix(logName)  # 检测日志格式
    logTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 日志时间
    log_management(f'{logTime}\n', logName, logMode)  # 记录日志时间

    is_compressFile(compressStyle)  # 检测压缩文件格式

    # time_list = [1, 60, 3600]  # 时间参数列表

    # ------------------程序开始------------------
    s_time = time.time()  # 起始时间
    dev_index = eval(device_index) if device_index.isnumeric(
    ) else device_index  # 设备选择 (usb 0,1,2; rtsp)
    cap = cv2.VideoCapture(dev_index)  # 设备连接
    is_capOpened = cap.isOpened()  # 判断摄像头是否正常启动

    if is_capOpened:  # 设备连接成功
        print(f'摄像头连接成功！')
        bufferSize = cap.get(cv2.CAP_PROP_BUFFERSIZE)
        # cap.set(cv2.CAP_PROP_BUFFERSIZE,10) # 1-10

        frame_width = cap.get(3)  # 帧宽度
        frame_height = cap.get(4)  # 帧高度
        fps = cap.get(5)  # 帧率
        print(f'宽度：{frame_width}, 高度：{frame_height}， FPS：{fps}， 缓存数：{bufferSize}')
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        frame_savePath = ""  # 保存路径
        if is_autoSaveFrame or is_handSaveFrame:
            # 帧保存路径管理
            frame_savePath = increment_path(
                Path(f"{frame_saveDir}") / frame_dirName, exist_ok=False)  # 增量运行
            frame_savePath.mkdir(parents=True, exist_ok=True)  # 创建目录

        frame_num = 0  # 总帧数
        frame_hand_num = 0  # 手动保存帧数
        while(is_capOpened):
            wait_key = cv2.waitKey(20) & 0xFF  # 键盘监听
            _, frame = cap.read()  # 捕获画面
            frame_num += 1  # 帧计数
            print(f'帧ID：{frame_num}')  # 输出帧ID信息
            cv2.imshow(OWS_VERSION, frame)  # 显示画面

            if (is_autoSaveFrame):  # 自动保存
                if (auto_frameNum > 0 and frame_num > auto_frameNum):
                    # 设置自动最大保存帧数
                    frame_num -= 1  # 修复帧数显示问题
                    break
                if (frame_num % frame_nSave == 0):  # 每隔n帧保存一次
                    frame_opt(frame, frame_savePath, frame_num, is_resizeFrame, resize_frame, resizeRatio_frame,
                              frame_namePrefix, frame_saveStyle, jpg_quality, png_quality)
            if (is_handSaveFrame):  # 手动保存
                if wait_key == ord(frame_capKey):  # 保存键
                    frame_hand_num += 1  # 手动帧计数
                    frame_opt(frame, frame_savePath, frame_num, is_resizeFrame, resize_frame, resizeRatio_frame,
                              frame_namePrefix, frame_saveStyle, jpg_quality, png_quality)

            if wait_key == ord(quit_key):  # 退出 ord：字符转ASCII码
                break
            if wait_key == ord(pause_key):
                print(f'已暂停！按任意键继续。。。')
                cv2.waitKey(0)  # 暂停，按任意键继续

        if (is_autoSaveFrame):
            # 帧保存信息（自动版）
            frameSaveMsg = f'自动版：共计{frame_num}帧，已保存在：{frame_savePath}'
            print(frameSaveMsg)
            log_management(f'{frameSaveMsg}\n', logName, logMode)  # 记录帧保存信息
        elif (is_handSaveFrame):
            # 帧保存信息（手动版）
            frameSaveMsg = f'手动版：共计{frame_hand_num}帧，已保存在：{frame_savePath}'
            print(frameSaveMsg)
            log_management(f'{frameSaveMsg}\n', logName, logMode)  # 记录帧保存信息

        cap.release()  # 释放缓存资源
        cv2.destroyAllWindows()  # 删除所有窗口
    else:  # 连接设备失败
        print(f'摄像头连接异常！')

    # ------------------程序结束------------------
    print(f'程序结束！')
    e_time = time.time()  # 终止时间
    total_time = e_time - s_time  # 程序用时
    # outTimeMsg = f'用时：{total_time/time_list[0]:.3f}秒, {total_time/time_list[1]:.3f}分, {total_time/time_list[2]:.3f}小时' # 适用于细微记录
    outTimeMsg = f'用时：{time_format(total_time)}' # 格式化时间格式，便于观察
    print(outTimeMsg)
    log_management(f'{outTimeMsg}\n', logName, logMode)  # 记录用时

    # ------------------压缩文件------------------
    if (is_compress and (is_autoSaveFrame or is_handSaveFrame)):
        webcam_compress(compressStyle, is_autoCompressName,
                        f'{ROOT_PATH}/{compressName}.{compressStyle}', frame_savePath, compressMode)


def main(args):
    device_index = args.device
    quit_key = args.quit
    is_autoSaveFrame = args.is_autoSaveFrame
    is_handSaveFrame = args.is_handSaveFrame
    frame_saveDir = args.frame_saveDir
    frame_dirName = args.frame_dirName
    frame_nSave = args.frame_nSave
    frame_capKey = args.frame_capKey
    resize_frame = args.resize_frame
    is_resizeFrame = args.is_resizeFrame
    resizeRatio_frame = args.resizeRatio_frame
    frame_namePrefix = args.frame_namePrefix
    frame_saveStyle = args.frame_saveStyle
    jpg_quality = args.jpg_quality
    png_quality = args.png_quality
    pause_key = args.pause
    auto_frameNum = args.auto_frameNum

    # 日志
    logName = args.logName
    logMode = args.logMode

    # 压缩
    is_compress = args.is_compress
    compressStyle = args.compressStyle
    is_autoCompressName = args.is_autoCompressName
    compressName = args.compressName
    compressMode = args.compressMode

    argsYaml(args)  # 脚本参数

    # 调用webcam opencv
    webcam_opencv(device_index,
                  quit_key,
                  pause_key,
                  is_autoSaveFrame,
                  frame_saveDir,
                  frame_dirName,
                  frame_nSave,
                  auto_frameNum,
                  is_handSaveFrame,
                  frame_capKey,
                  is_resizeFrame,
                  resize_frame,
                  resizeRatio_frame,
                  frame_namePrefix,
                  frame_saveStyle,
                  jpg_quality,
                  png_quality,
                  logName,
                  logMode,
                  is_compress,
                  compressStyle,
                  is_autoCompressName,
                  compressName,
                  compressMode)


if __name__ == '__main__':
    args = parse_args()
    main(args)
