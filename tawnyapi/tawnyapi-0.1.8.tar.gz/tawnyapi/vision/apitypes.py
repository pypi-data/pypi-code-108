
from enum import Enum


class ImageInputType(str, Enum):
    RAW = 'RAW'
    FACE = 'FACE'
    FACE_EMBEDDING = 'FACE_EMBEDDING'


class ImageAnnotationFeatures(str, Enum):
    FACE_DETECTION = 'FACE_DETECTION'
    FACE_LANDMARKS = 'FACE_LANDMARKS'
    FACE_EMOTION = 'FACE_EMOTION'
    FACE_DESCRIPTOR = 'FACE_DESCRIPTOR'
    ATTENTION = 'ATTENTION'
    HEAD_POSE = 'HEAD_POSE'


class SdkVersion(str, Enum):
    V_1_4 = 'V_1_4'
