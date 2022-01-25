import cv2
import os
import time
import numpy as np
from dataclasses import dataclass


@dataclass
class VideoFile:
    input_file: str

    # output_path: str

    def __post_init__(self):
        self._video = cv2.VideoCapture(self.input_file)
        self._fps = self._video.get(cv2.CAP_PROP_FPS)
        self._resolution = self._video.get(cv2.CAP_PROP_FRAME_WIDTH), self._video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._frame_count = int(self._video.get(cv2.CAP_PROP_FRAME_COUNT))
        self._duration = self._frame_count / self._fps

    @property
    def video(self) -> cv2.VideoCapture:
        return self._video

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def resolution(self) -> tuple:
        """ Returns a (width, height) tuple """
        return self._resolution

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def duration(self) -> float:
        return self._duration

    def get_frame(self, frame_number: int) -> np.ndarray:
        self._video.set(1, frame_number)
        ret, frame = self._video.read()
        return frame

    def release(self) -> None:
        self._video.release()


@dataclass
class VideoCaptions:
    video_file: VideoFile
    shots = 9

    def __post_init__(self):
        # Ίσως να τα κάνω cashed properties
        self._captions_frame_numbers = self.get_captions_frame_numbers()
        self._captions = self.get_captions()

    @property
    def captions_frame_numbers(self) -> list:
        return self._captions_frame_numbers

    @property
    def captions(self) -> list:
        return self._captions

    def get_captions_frame_numbers(self) -> list:
        """
        Divide the length of the video and get the frame numbers for the captions
        No captions are taken at the first and the last frames
        """
        cfn = list(np.linspace(0, self.video_file.frame_count, self.shots + 2).astype(int))
        return cfn[1:-1]

    def get_captions(self) -> list:
        caps = []
        cfn = self._captions_frame_numbers
        for cf in cfn:
            caps.append(self.video_file.get_frame(cf))

        return caps

    def save_all_captions(self, directory) -> None:
        for frame_number, cap in zip(self._captions_frame_numbers, self._captions):
            cv2.imwrite(directory + '\\frame' + str(frame_number) + '.png', cap)

    def concatenate9(self):
        imgs = self._captions
        conc_image = cv2.vconcat([cv2.hconcat([imgs[0], imgs[1], imgs[2]]),
                                  cv2.hconcat([imgs[3], imgs[4], imgs[5]]),
                                  cv2.hconcat([imgs[6], imgs[7], imgs[8]])])
        return conc_image

    def resize9(self, width=1024):
        conc_image = self.concatenate9()
        height = int(self.video_file.resolution[1] * width / self.video_file.resolution[0])
        dim = (width, height)
        resized_image = cv2.resize(conc_image, dim, interpolation=cv2.INTER_AREA)
        return resized_image

    def save9(self, filename, width=1024):
        img = self.resize9(width)
        cv2.imwrite(filename + '.jpg', img)


def main():
    v = VideoFile(input_file=r'E:\downloads\!tor\movies\Life Of Brian.1979.BRRip.XviD.AC3[GTRD-movies].avi')
    print(v.fps)
    print(v.resolution)
    print(v.frame_count)
    print(v.duration)

    vc = VideoCaptions(video_file=v)
    # vc.save_all_captions(r'D:\test\test\out')
    # im.fromarray(vc.captions[2])
    vc.save9(r'D:\test\test\out\aaaa', 1024)

    # v2 = VideoFile(input_file=r'D:\test\test\0202.mp4')
    #
    # print(v2.__dict__)
    #
    # fr1 = v2.get_frame(2000)
    # fr2 = v2.get_frame(3000)
    # fr3 = v2.get_frame(4000)
    # fr4 = v2.get_frame(5000)
    #
    # ch_im = cv2.hconcat([fr1, fr2])
    #
    # cv2.imshow("test", fr1)
    # cv2.waitKey()
    # cv2.imshow("test", fr2)
    # cv2.waitKey()
    # cv2.imshow("test2", ch_im)
    # cv2.waitKey()
    # cv2.imwrite(r'D:\test\test\0202.jpg', fr1)
    # cv2.imwrite(r'D:\test\test\0203.jpg', ch_im)
    # cv2.waitKey()
    # cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

