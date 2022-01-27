import os
import cv2
import numpy as np
import logging
import os.path
import urllib.request
from .util import _get_temp_folder, _get_square_from_box, _box_norm


MODEL_LINKS = [
    {
        'type': 'caffemodel',
        'filename': 'res10_300x300_ssd_iter_140000.caffemodel',
        'url': 'https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel'},
    {
        'type': 'prototxt',
        'filename': 'deploy.prototxt',
        'url': 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt'},
]

logger = logging.getLogger(__name__)


class FaceDetector:

    def __init__(self, min_face_confidence=0.6):
        self.min_face_confidence = min_face_confidence
        caffemodel = ''
        prototxt = ''

        dirpath = _get_temp_folder()

        for entry in MODEL_LINKS:
            filename = os.path.join(dirpath, entry['filename'])

            if entry['type'] == 'prototxt':
                prototxt = filename

            if entry['type'] == 'caffemodel':
                caffemodel = filename

            if not os.path.isfile(filename):
                logging.info(
                    'downloading face detection model ...')
                try:
                    urllib.request.urlretrieve(entry['url'], filename)
                except Exception as inst:
                    logging.error(inst)
                    logging.error('Encountered unknown error. Continuing.')

        self.face_detector_model = cv2.dnn.readNetFromCaffe(
            prototxt, caffemodel)

    def detect_face(self, frame, include_meta=False):
        x1, y1, x2, y2 = (0, 0, 0, 0)
        confidence = 0.0
        faces = []

        faces = self.detect_faces(frame, include_meta=True)

        for face in faces:
            b_x1, b_y1, b_x2, b_y2 = _get_square_from_box(
                face['bounding_box'])
            if _box_norm(b_x1, b_y1, b_x2, b_y2) > _box_norm(x1, y1, x2, y2):
                x1, y1, x2, y2 = (b_x1, b_y1, b_x2, b_y2)
                confidence = face['confidence']

        if include_meta:
            return {
                'bounding_box': (x1, y1, x2, y2),
                'confidence': confidence
            }

        return x1, y1, x2, y2

    def detect_faces(self, bgr_frame, include_meta=False):
        (h, w) = bgr_frame.shape[:2]
        # bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        blob = cv2.dnn.blobFromImage(cv2.resize(bgr_frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        self.face_detector_model.setInput(blob)
        detections = self.face_detector_model.forward()
        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence >= self.min_face_confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                if include_meta:
                    faces.append({
                        'bounding_box': (x1, y1, x2, y2),
                        'confidence': confidence
                    })
                else:
                    faces.append((x1, y1, x2, y2))
        return faces
