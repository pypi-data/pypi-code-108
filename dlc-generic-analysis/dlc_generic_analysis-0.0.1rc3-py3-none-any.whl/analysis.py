import os
import pandas
import abc


class Analysis(abc.ABC):
    def __init__(self, h5_path: str, dlc_scorer: str, startframe: int = 0, endframe: int = None):
        """
        Analysis:
        :param h5_path: the path of the h5 file created by analyze_videos
        :param dlc_scorer: the DeepLabCut model name
        :param startframe: the first frame of video to analyze
        :param endframe: the last frame of video to analyze
        """
        if not os.path.isfile(h5_path):
            raise FileNotFoundError(h5_path)
        self.df = pandas.read_hdf(h5_path)[dlc_scorer]
        self.start_frame = startframe
        if endframe is None:
            self.end_frame = len(self.df.index)
        else:
            self.end_frame = endframe
        assert self.end_frame > self.start_frame
        self.nframes = self.end_frame - self.start_frame
        self.outpath = os.path.split(h5_path)[0]
        self.outpath = os.path.join(h5_path, "analyzed_videos")

    @abc.abstractmethod
    def draw(self):
        """
        draw geometries from the analysis on the video and return a new video
        """
        pass

    @abc.abstractmethod
    def write_csv(self):
        """write data from the analysis to a file"""
        pass
