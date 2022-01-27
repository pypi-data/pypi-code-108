"""
@Author https://github.com/thearyadev
"""


class SexyThumbnailGenerator:
    """
    Takes a video and extracts frames at specified {increment}.
    Reduction: Amount of start and end of video to not consider. Default 30%
    Sends a list of those frames to a Explicit content checker.
    This returns a list of the types of explicit content are in the frame
    The frame is then given a sexiness score based on the results of the dataset comparison

    Save() save image to directory.
    """
    import cv2
    from . import NudeDetector

    def __init__(self, video, reduction=0.3):
        self.CAPTURE = self.cv2.VideoCapture(video)
        self.detect = self.NudeDetector().detect
        self.TOTAL_FRAMES = self.CAPTURE.get(self.cv2.CAP_PROP_FRAME_COUNT)
        self.reduction = int(reduction * self.TOTAL_FRAMES)
        self.CURRENT_FRAME = self.reduction
        self.FINAL_FRAME = self.TOTAL_FRAMES - self.reduction
        self.SELECTION = None
        self.ALL_FRAMES = []

    def generateSelection(self, increment=6000):
        self.INCREMENT = increment
        __extracted_frames__ = self.__get_frames__()
        __temp_best_frame__ = {"frame": None, "score": None}
        for frame in __extracted_frames__:
            __temp_best_frame__['frame'], __temp_best_frame__['score'] = frame, self.enumerate(self.check(frame))
            self.ALL_FRAMES.append((__temp_best_frame__['frame'], __temp_best_frame__['score']))
        self.SELECTION = __temp_best_frame__
        self.CURRENT_FRAME = self.reduction
        return {"score": self.SELECTION['score']}

    @staticmethod
    def enumerate(data):
        score = 0
        if "FACE_F" in data: score += 2
        if "EXPOSED_GENITALIA_F" in data: score += 6
        if "COVERED_GENITALIA_F" in data: score += 4
        if "EXPOSED_ANUS" in data: score += 3
        if "EXPOSED_BREAST_F" in data: score += 2
        if "COVERED_BREAST_F" in data: score += 1
        return score

    def check(self, frame):
        tags = [tag['label'] for tag in self.detect(frame)]
        return tags

    def save(self, location="./image.jpg"):
        try:
            self.cv2.imwrite(location, self.SELECTION['frame'])
            return True
        except:
            return False

    def __get_frames__(self):
        __extracted_frames__ = []
        while True:
            try:
                self.CAPTURE.set(1, self.CURRENT_FRAME)
                _, frame = self.CAPTURE.read()
                if self.CURRENT_FRAME > self.FINAL_FRAME:
                    break
                self.__increment__()
                __extracted_frames__.append(frame)

            except Exception as e:
                raise e
        return __extracted_frames__

    def __increment__(self):
        self.CURRENT_FRAME += self.INCREMENT


if __name__ == "__main__":
    x = SexyThumbnailGenerator("X:\Aryan\Media\Film Database\\00590\\film.mp4")
    x.generateSelection()
    x.save("./image.png")
