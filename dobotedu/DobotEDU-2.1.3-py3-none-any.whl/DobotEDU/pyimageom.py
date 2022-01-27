from typing import List, Any
from .pause.pauselab import PauseLab, pause


class InvalidDataError(Exception):
    def __init__(self, error: str):
        super().__init__(error)


class ImageGroupError(Exception):
    def __init__(self, error: str):
        super().__init__(error)


class Pyimageom(PauseLab):
    def __init__(self, rpc_adapter):
        self._r_client = rpc_adapter

    @pause
    def image_cut(self, img_base64: str):
        if len(img_base64) != 0:
            return self._r_client.image_cut(img_base64=img_base64)
        else:
            raise InvalidDataError("img_base64 cannot be empty.")

    @pause
    def feature_image_classify(self, img_base64s: List[Any], lables: List[int],
                               class_num: int, flag: int):
        return self._r_client.feature_image_classify(img_base64s=img_base64s,
                                                     lables=lables,
                                                     class_num=class_num,
                                                     flag=flag)

    @pause
    def feature_image_group(self, img_base64: str):
        if len(img_base64) != 0:
            try:
                res = self._r_client.feature_image_group(img_base64=img_base64)
            except Exception as e:
                raise ImageGroupError(
                    f"Please add at least two sets of data with no less than 3 photos in each group. ERROR: {e}"
                )
            return res
        else:
            raise InvalidDataError("img_base64 cannot be empty.")

    @pause
    def find_chessboard_corners(self, img_base64: str):
        if len(img_base64) != 0:
            return self._r_client.find_chessboard_corners(
                img_base64=img_base64)
        else:
            raise InvalidDataError("img_base64 cannot be empty.")

    @pause
    def color_image_cut(self, img_base64: str):
        if len(img_base64) != 0:
            return self._r_client.color_image_cut(img_base64=img_base64)
        else:
            raise InvalidDataError("img_base64 cannot be empty.")

    @pause
    def color_image_classify(self, img_base64s: List[Any], lables: List[int],
                             class_num: int, flag: int):
        return self._r_client.color_image_classify(img_base64s=img_base64s,
                                                   lables=lables,
                                                   class_num=class_num,
                                                   flag=flag)

    @pause
    def color_image_group(self, img_base64: str):
        if len(img_base64) != 0:
            try:
                res = self._r_client.color_image_group(img_base64=img_base64)
            except Exception as e:
                raise ImageGroupError(
                    f"Please add at least two sets of data with no less than 3 photos in each group. ERROR: {e}"
                )
            return res
        else:
            raise InvalidDataError("img_base64 cannot be empty.")

    @pause
    def set_background(self, img_base64: str):
        if len(img_base64) != 0:
            return self._r_client.set_background(img_base64=img_base64)
        else:
            raise InvalidDataError("img_base64 cannot be empty.")