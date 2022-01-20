from pathlib import Path
from pypicgo.core.base.plugin import BeforePlugin
from pypicgo.core.base.file import UploadFile
from blind_watermark import WaterMark

BASE_DIR = Path(__file__).resolve().parent


class BlindWaterMarkPlugin(BeforePlugin):
    name = 'blind-watermark'

    def __init__(self, mark: str, **kwargs):
        super().__init__(**kwargs)
        self.mark = mark

    def execute(self, file: UploadFile) -> UploadFile:
        filepath = file.tempfile.resolve()
        filename = file.tempfile.name
        bwm = WaterMark()
        bwm.read_img(str(filepath))
        bwm.read_wm(self.mark, mode='str')
        after_filepath = BASE_DIR.joinpath('temp')
        if not after_filepath.exists():
            after_filepath.mkdir(parents=True)
        after_filepath = after_filepath.joinpath(filename)
        bwm.embed(str(after_filepath.resolve()))
        file.tempfile = after_filepath
        return file
