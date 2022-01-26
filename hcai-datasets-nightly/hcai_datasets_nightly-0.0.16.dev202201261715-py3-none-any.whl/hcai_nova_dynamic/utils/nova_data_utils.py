import cv2
import numpy as np
import os
import tensorflow_datasets as tfds
import tensorflow as tf
from hcai_datasets.hcai_nova_dynamic.utils import nova_types as nt
from hcai_datasets.hcai_nova_dynamic.utils.ssi_stream_utils import Stream
from hcai_datasets.hcai_nova_dynamic.utils.nova_utils import merge_role_key, split_role_key
from typing import Union
from abc import ABC, abstractmethod

class Data(ABC):

    lazy_connector = tfds.features.FeaturesDict({
        'frame_start': tf.dtypes.float32,
        'frame_end': tf.dtypes.float32,
        'file_path': tfds.features.Text()
    })


    def __init__(self,  role: str = '', name: str = '', file_ext: str = 'stream', sr: int = 0, data_type: nt.DataTypes = None, is_valid: bool = True, sample_data_path: str = '', lazy_loading: bool = False):
        self.role = role
        self.name = name
        self.is_valid = is_valid
        self.sr = sr
        self.file_ext = file_ext
        self.lazy_loading = lazy_loading
        self.data_type = data_type

        # Set when populate_meta_info is called
        self.sample_data_shape = None
        self.tf_data_type = None
        self.meta_loaded = False

        # Set when open_file_reader is called
        self.file_path = None
        self.file_reader = None
        self.dur = None

        if sample_data_path:
            self.populate_meta_info(sample_data_path)

    def data_stream_opend(self):
        if not self.file_reader:
            print('No datastream opened for {}'.format(merge_role_key(self.role, self.name)))
            raise RuntimeError('Datastream not loaded')


    def get_tf_info(self):
        if self.meta_loaded:
            if self.lazy_loading:
                feature_connector = self.lazy_connector
                key = merge_role_key(self.role, self.name)
                return (key, feature_connector)
            else:
                return self.get_tf_info_hook()
        else:
            print('Meta data has not been loaded for file {}. Call get_meta_info() first.'.format(
                merge_role_key(self.role, self.name)))


    def get_sample(self, frame_start: int, frame_end: int):
        """
        Returns the sample for the respective frames. If lazy loading is true, only the filepath and frame_start, frame_end will be returned.
        """
        if self.lazy_loading:
            return {
                'frame_start': frame_start,
                'frame_end': frame_end,
                'file_path': self.file_path
            }
        else:
            return self.get_sample_hook(frame_start, frame_end)

    def open_file_reader(self, path: str):
        self.file_path = path
        self.open_file_reader_hook(path)

    @abstractmethod
    def get_tf_info_hook(self):
        """
        Returns the features for this datastream to create the DatasetInfo for tensorflow
        """
        ...

    @abstractmethod
    def get_sample_hook(self, start_frame: int, end_frame: int):
        """
        Returns a data chunk from start frame to end frame
        """
        ...

    @abstractmethod
    def open_file_reader_hook(self, path: str):
        """
        Opens a filereader for the respective datastream. Sets attributes self.file_reader and self.dur
        """
        ...

    @abstractmethod
    def populate_meta_info(self, path: str):
        """
        Opens a data sample from the provided path to extract additional data that is not in the database
        """
        ...

    @abstractmethod
    def close_file_reader(self):
        """
        Closes a filereader for the respective datastream
        """
        ...


class AudioData(Data):
    pass


class VideoData(Data):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_tf_info_hook(self) -> (str, tfds.features.Sequence):
        feature_connector = tfds.features.Sequence(
        tfds.features.Image(shape=self.sample_data_shape, dtype=np.uint8))
        return merge_role_key(self.role, self.name), feature_connector

    def get_sample_hook(self, frame_start_ms: int, frame_end_ms: int):
        start_frame = frame_start_ms / 1000 * self.sr
        end_frame = frame_end_ms / 1000 * self.sr
        length = int(end_frame - start_frame)

        self.file_reader.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        chunk = np.zeros((length, ) + self.sample_data_shape, dtype=np.uint8)

        for i in range(length):
            ret, frame = self.file_reader.read()

            if not ret:
                raise IndexError('Video frame {} out of range'.format(i))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            chunk[i] = frame

        return chunk

    def open_file_reader_hook(self, path: str):
        if not os.path.isfile(path):
            print('Session file not found at {}.'.format(path))
            raise FileNotFoundError()
        self.file_reader = cv2.VideoCapture(path)
        fps = self.file_reader.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(self.file_reader.get(cv2.CAP_PROP_FRAME_COUNT))
        self.dur = frame_count / fps

    def populate_meta_info(self, path: str):
        if not os.path.isfile(path):
            print('Sample file not found at {}. Can\'t load metadata.'.format(path))
            raise FileNotFoundError()
        file_reader = cv2.VideoCapture(path)
        width = int(file_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(file_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        depth = 3
        self.sample_data_shape = (height, width, depth)
        self.meta_loaded = True

    def close_file_reader(self):
        return self.file_reader.release()


class StreamData(Data):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_tf_info_hook(self) -> (str, tfds.features.Sequence):
        feature_connector = tfds.features.Sequence(tfds.features.Tensor(shape=self.sample_data_shape, dtype=self.tf_data_type))
        return merge_role_key(self.role, self.name), feature_connector

    def get_sample_hook(self, frame_start_ms: int, frame_end_ms: int):
        try:
            self.data_stream_opend()
            start_frame = milli_seconds_to_frame(self.sr, frame_start_ms)
            end_frame = milli_seconds_to_frame(self.sr, frame_end_ms)
            return self.file_reader.data[start_frame:end_frame]
        except RuntimeError:
            print('Could not get chunk {}-{} from data stream {}'.format(frame_start_ms, frame_end_ms, merge_role_key(self.role, self.name)))

    def open_file_reader_hook(self, path: str) -> bool:
        stream = Stream(path)
        if stream:
            self.file_reader = stream
            self.dur = stream.data.shape[0] / stream.sr
            return True
        else:
            print('Could not open Stream {}'.format(str))
            return False

    def close_file_reader(self):
        return True

    def populate_meta_info(self, path: str):
        stream = Stream().load_header(path)
        self.sample_data_shape = (stream.dim,)
        self.tf_data_type = stream.tftype
        self.meta_loaded = True

##########################
# General helper functions
##########################

def frame_to_seconds(sr: int, frame: int) -> float:
    return frame / sr


def seconds_to_frame(sr: int, time_s: float) -> int:
    return round(time_s * sr)


def milli_seconds_to_frame(sr: int, time_ms: int) -> int:
    return seconds_to_frame(sr=sr, time_s= time_ms / 1000)


def parse_time_string_to_ms(frame: Union[str, int, float]) -> int:
    # if frame is specified milliseconds as string
    if str(frame).endswith('ms'):
        try:
            return int(frame[:-2])
        except ValueError:
            raise ValueError('Invalid input format for frame in milliseconds: {}'.format(frame))
    # if frame is specified in seconds as string
    elif str(frame).endswith('s'):
        try:
            frame_s = float(frame[:-1])
            return int(frame_s * 1000)
        except ValueError:
            raise ValueError('Invalid input format for frame in seconds: {}'.format(frame))
    # if type is float we assume the input will be seconds
    elif isinstance(frame, float) or '.' in str(frame):
        try:
            print('WARNING: Automatically inferred type for frame {} is float.'.format(frame))
            return int(1000 * float(frame))
        except ValueError:
            raise ValueError('Invalid input format for frame: {}'.format(frame))
    # if type is int we assume the input will be milliseconds
    elif isinstance(frame, int) or (isinstance(frame, str) and frame.isdigit()):
        try:
            print('WARNING: Automatically inferred type for frame {} is int.'.format(frame))
            return int(frame)
        except ValueError:
            raise ValueError('Invalid input format for frame: {}'.format(frame))
