import argparse
import multiprocessing
import os
import ccdt.video_tool.split


def get_args():
    parser = argparse.ArgumentParser('视频按帧切片（需要传入两个参数videos_dir，imgs_dir）')
    parser.add_argument('--input_dir',
                        default=r'C:/Users/54071/Desktop/55/data/rename_video_test',
                        help='需要切片的视频路径(支持中文和英文)')
    parser.add_argument('--output_dir',
                        default=r'C:/Users/54071/Desktop/55/data/rename_video_test/output_video',
                        help='图片保存路径')
    parser.add_argument('--file_types',
                        default=['.mp4', '.MP4', '.mov', '.avi', '.MOV', '.264', '.dav', '.wmv', '.AVI', '.avi',
                                 '.webm', '.mkv', '.mkv', '.WMV', '.FLV', '.flv', '.MPG', '.mpg'],
                        help='视频文件格式')
    parser.add_argument('--image_format', default='jpg', help='图片格式')
    parser.add_argument('--interval', default=50, help='几帧切一次')
    parser.add_argument('--function', type=str, help="输入操作功能参数:split只能输入单个")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    if args.function == 'split':
        videos_path = ccdt.Split.get_videos_path(args.input_dir, args.file_types)
        # 创建进程池
        po = multiprocessing.Pool(20)
        # 创建一个队列
        q = multiprocessing.Manager().Queue()
        for video_path in videos_path[3]:
            new_path = video_path.replace(args.input_dir, args.output_dir)
            dir_name = os.path.dirname(new_path)
            file_name = os.path.basename(new_path)
            file_prefix = os.path.splitext(file_name)[-2]
            output_dir = os.path.join(dir_name, file_prefix)
            # 向进程池中添加,截取视频中的每一帧图片的任务
            po.apply_async(ccdt.Split.video_loader, args=(q, video_path, args.interval, output_dir))
        po.close()
        # po.join()  # 加上这个打印进度就会一次性打印完毕，不会分段打印
        all_file_num = len(videos_path[3])
        copy_ok_num = 0
        while True:
            file_name = q.get()
            print("\r已经完成提取视频帧：%s" % file_name)
            copy_ok_num += 1
            print("\r提取视频帧的进度为：%.2f %%" % (copy_ok_num * 100 / all_file_num), end="")
            if copy_ok_num >= all_file_num:
                break


if __name__ == '__main__':
    main()
