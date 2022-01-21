import os
#os.environ["IMAGEMAGICK_BINARY"] = "magick"
import uuid
from bgeditor.dao.FFmpeg import create_source_can_loop, create_loop
from bgeditor.dao.Lyric import Lyric
from bgeditor.common.utils import download_file, get_dir
import tempfile
from bgeditor.dao.Component import create_video, create_image

class BGEditor():
    def __init__(self):
        self.root_dir = tempfile.TemporaryDirectory()

    def create_source_can_loop_by_file(self, ori_file, is_delete=True):
        if ori_file:
            path_loop = create_source_can_loop(self.root_dir.name, ori_file, is_delete)
            return path_loop
        else:
            return None

    def download_video(self, url):
        return download_file(url, self.root_dir.name)


    def loop_video(self, ori_file, duration, can_loopable):
        return create_loop(ori_file, duration, can_loopable)


    def create_lyric_bg_video(self, lyric_data, font_url, font_size, color, duration, is_optimize= False, w=1920, h=1080):
        lyric = Lyric(lyric_data, font_url, font_size, color, duration, w, h)
        if lyric.init():
            if is_optimize:
                lyric.optimize_font()
            return lyric.make()
        return None

    def create_video_json(self, list_comp_data, job_id, mf_server="http://api-magicframe.automusic.win/"):
        #path_vid = self.root_dir.name + "/final-vid-" + str(uuid.uuid4()) + ".avi"
        path_vid = os.path.join(get_dir('results'), "final-vid-" + str(uuid.uuid4()) + ".mp4")
        path_vid = create_video(list_comp_data, path_vid, job_id, mf_server)
        return path_vid
    def create_image_json(self, list_comp_data):
        #path_vid = self.root_dir.name + "/final-vid-" + str(uuid.uuid4()) + ".avi"
        path_vid = os.path.join(get_dir('results'), "final-image-" + str(uuid.uuid4()) + ".png")
        path_vid = create_image(list_comp_data, path_vid, 0)
        return path_vid

    def close(self):
        # os.system("rm -rf /tmp/download/*")
        # os.system("rm -rf /tmp/coolbg_ffmpeg/*")
        # os.system("rm -rf /tmp/results/*")
        self.root_dir.cleanup()




