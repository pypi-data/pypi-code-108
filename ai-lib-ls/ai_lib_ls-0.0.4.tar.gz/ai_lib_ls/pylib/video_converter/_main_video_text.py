"""
程序主入口
"""
# from video_converter import convert_to_text
from ai_lib_ls.pylib.video_converter import convert_to_text

if __name__ == '__main__':
    text_info = convert_to_text(
        source_media_path=r'/Users/apple/Qsync/gitNew/推荐数字系统/test_video/video_tencent_pro_15357682_1642674554.mp4')

    print(text_info)
