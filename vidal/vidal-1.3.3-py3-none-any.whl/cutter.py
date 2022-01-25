import argparse
import asyncio
import concurrent.futures

from functools import partial
from pathlib import Path

from tqdm import tqdm
import cv2
import numpy as np

__all__ = ["VideoFrame", "one_video", "many_videos"]


VIDEO_SUFFIX = [".mp4", ".3gp", ".avi"]


class VideoFrame:
    def __new__(cls, *args, **kwargs):
        self = cls._from_parts(*args, **kwargs)
        return self

    @classmethod
    def _from_parts(cls, *args, **kwargs):
        self = object.__new__(cls)
        self.filename = cls._parse_args(*args, **kwargs)
        self._init()
        return self

    def _init(self):
        self._video = cv2.VideoCapture(self.filename)
        self.video_len = int(self._video.get(cv2.CAP_PROP_FRAME_COUNT))

    @classmethod
    def _parse_args(cls, *args, **kwargs):
        args_cnt = len(args)
        if args_cnt == 1:
            filename = args[0]
        elif args_cnt == 0:
            filename = kwargs.get("filename")

        return str(filename)

    def __init__(self, filename: str):
        self._pos_frame = -1

    @property
    def pos_frame(self):
        # Real Pos
        return self._pos_frame + 1

    def __len__(self):
        return self.video_len

    def __iter__(self):
        while True:
            rat, frame = self._video.read()
            if rat:
                yield frame
            else:
                break

    def __getitem__(self, idx):
        if isinstance(idx, int):
            self._video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            rat, frame = self._video.read()
            self._video.set(cv2.CAP_PROP_POS_FRAMES, self._pos_frame)
            if rat:
                return frame
            else:
                IndexError

        if isinstance(idx, slice):
            result = []
            start, stop, step = self._slice(idx)

            frame_num = start
            next_frame_num = frame_num

            self._video.set(cv2.CAP_PROP_POS_FRAMES, idx.start)
            while frame_num < stop:
                rat, frame = self._video.read()
                try:
                    if rat:
                        if frame_num == next_frame_num:
                            next_frame_num += step
                            yield frame
                        # stride값에 매칭되지 않으면 다음프레임으로 넘어간다.
                        frame_num += 1
                    elif rat == False:
                        break
                except:
                    raise IndexError

    def _slice(self, idx: slice):
        start = idx.start if idx.start else 0
        stop = idx.stop if idx.stop else self.video_len
        step = idx.step if idx.step else 1
        return start, stop, step

    def _stride(self, frame_num):
        return frame_num % self.stride == 0


def imwrite(filename: Path, frame, params=None):
    result, encoded_img = cv2.imencode(filename.suffix, frame, params)
    if result:
        with open(str(filename), mode="w+b") as f:
            encoded_img.tofile(f)


async def make_image(video_dir, frame, frame_num):
    video_dir = Path(video_dir)
    image_path = (
        video_dir.parent / video_dir.stem / f"{video_dir.stem}_{int(frame_num)}.jpg"
    )
    loop = asyncio.get_event_loop()
    imwrite_func = partial(imwrite, image_path, frame)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, imwrite_func)


async def one_video(video_path, stride):
    video_frames = VideoFrame(video_path)
    try:
        await asyncio.wait(
            [
                make_image(video_path, frame, idx * stride + 1)
                for idx, frame in enumerate(video_frames[::stride])
            ]
        )
    except:
        return


async def many_videos(video_paths, stride):
    for video in tqdm(video_paths):
        await one_video(video, stride)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path of file or folder", type=str)
    parser.add_argument(
        "stride",
        help="Stride Frames",
        type=int,
    )
    loop = asyncio.get_event_loop()

    args = parser.parse_args()

    if Path(args.path).is_dir():
        videos = [
            video for video in Path(args.path).glob("*") if video.suffix in VIDEO_SUFFIX
        ]
        for video in videos:
            video.with_suffix("").mkdir(exist_ok=True)
        loop.run_until_complete(many_videos(videos, args.stride))
    else:
        Path(args.path).with_suffix("").mkdir(exist_ok=True)
        loop.run_until_complete(one_video(args.path, args.stride))


if __name__ == "__main__":
    video_frame = VideoFrame("test.mp4")
    for i in video_frame[::10]:
        print(i.shape)
