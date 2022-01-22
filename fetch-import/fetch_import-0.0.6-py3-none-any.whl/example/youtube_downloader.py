import shutil
from typing import List

from yt_dlp import YoutubeDL

from fetch_import import _import

_import(globals(),
        "https://raw.githubusercontent.com/zmaplex/fetch_import/main/example/job_plugin.py",
        "JobPlugin", ["JobPlugin"])


class Subtitle:
    def __init__(self, lang, url, suffix):
        self.lang = lang
        self.url = url,
        self.suffix = suffix

    def __str__(self):
        return f"{self.lang}.{self.suffix}"

    @staticmethod
    def _format_conversion(old_suffix, new_suffix):
        if new_suffix.lower() == 'srt':
            pass
        else:
            pass

    def to_srt(self):
        self._format_conversion(self.suffix, 'srt')


class VideoInfoRes:

    def __init__(self, **kwargs):
        self.vid = kwargs.get('id')
        self.title = kwargs.get('title')
        self.uploader = kwargs.get('uploader')
        self.uploader_id = kwargs.get('uploader_id', None)
        self.thumbnail = kwargs.get('thumbnail', None)
        self.sub_url_list: List[Subtitle] = kwargs.get('sub_url_list', [])
        self.filesize = kwargs.get("filesize_approx", 0)
        self.ext = kwargs.get('ext')
        print(f"Get:{self.__str__()}, Estimated download size:{self.filesize / 1024 / 1024} MB")

    def __str__(self):
        return f"{self.title}.{self.ext}"


class YoutubeDownloader(JobPlugin):
    ydl_opts: dict = {'proxy': '127.0.0.1:7890',
                      'f': 'bestvideo+bestaudio[ext=m4a]',
                      'merge-output-format': 'mp4'}
    url: str = ''
    res: VideoInfoRes = ''
    save_tmp_path = None
    upload_sbc = {}
    authorization = ''

    @staticmethod
    def version():
        return 1

    @classmethod
    def plugin_name(cls):
        cls.__name__.__str__()

    def execution(self, **kwargs):
        self.__dict__.update(kwargs)
        self.ydl_opts = kwargs.get('ydl_opts', self.ydl_opts)
        self.res = self.format_video_information()
        self.download()

    def download(self):
        self.save_tmp_path = self.exec_dir + "/" + self.res.__str__()
        if 'outtmpl' not in self.ydl_opts:
            self.ydl_opts['outtmpl'] = self.save_tmp_path
        if 'ratelimit' not in self.ydl_opts:
            self.ydl_opts['ratelimit'] = 1024 * 1024 * 1024
        with YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

    def finish(self):
        print("doing somethings")

    def clean(self):
        shutil.rmtree(self.exec_dir)

    def format_video_information(self):
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
        return VideoInfoRes(**info)


if __name__ == '__main__':
    pass
