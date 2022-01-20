from __future__ import division, print_function, absolute_import

import os
from timeit import time
import warnings
import cv2
import numpy as np
from PIL import Image
from Sort.yolo import YOLO
from Sort.deep_sort import preprocessing, nn_matching
from Sort.deep_sort.detection import Detection
from Sort.deep_sort.tracker import Tracker
from Sort.tools import generate_detections as gdet
from collections import deque
from keras import backend

backend.clear_session()

pts = [deque(maxlen=30) for _ in range(9999)]
warnings.filterwarnings('ignore')

# initialize a list of colors to represent each possible class label
np.random.seed(100)
COLORS = np.random.randint(0, 255, size=(200, 3),
                           dtype="uint8")


class Sort(object):
    def __init__(self, model_path, anchors_path, classes_path, model_filename,
                 video_path, model_type='car', result_path='./results'):
        self.video_path = video_path
        self.model_type = model_type
        self.result_path = result_path
        self.yolo = YOLO(model_path, anchors_path, classes_path, model_type)
        self.model_filename = model_filename

    def train(self):
        video_full_path = self.video_path
        result_path = self.result_path
        filename = str(self.video_path).split('/')[-1].split('.')[0]
        type = self.model_type
        # print(video_full_path)
        # print(result_path)
        # print(filename)
        # print(type)
        start = time.time()
        # Definition of the parameters
        max_cosine_distance = 0.5  # 余弦距离的控制阈值
        nn_budget = None
        nms_max_overlap = 0.3  # 非极大抑制的阈值

        counter = []
        encoder = gdet.create_box_encoder(self.model_filename, batch_size=1)

        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
        tracker = Tracker(metric)

        writeVideo_flag = True
        video_capture = cv2.VideoCapture(video_full_path)

        if writeVideo_flag:
            # Define the codec and create VideoWriter object
            w = int(video_capture.get(3))
            h = int(video_capture.get(4))
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(result_path + '/' + filename + "_" + type + '_output.avi', fourcc, 15,
                                  (w, h))
            list_file = open('detection.txt', 'w')
            frame_index = -1

        fps = 0.0

        while True:

            ret, frame = video_capture.read()  # frame shape 640*480*3
            if ret != True:
                break
            t1 = time.time()

            # image = Image.fromarray(frame)
            image = Image.fromarray(frame[..., ::-1])  # bgr to rgb
            boxs, class_names = self.yolo.detect_image(image)
            features = encoder(frame, boxs)
            # score to 1.0 here).
            detections = [Detection(bbox, 1.0, feature) for bbox, feature in zip(boxs, features)]
            # Run non-maxima suppression.
            boxes = np.array([d.tlwh for d in detections])
            scores = np.array([d.confidence for d in detections])
            indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
            detections = [detections[i] for i in indices]

            # Call the tracker
            tracker.predict()
            tracker.update(detections)

            i = int(0)
            indexIDs = []
            c = []
            boxes = []
            for det in detections:
                bbox = det.to_tlbr()
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255), 2)

            for track in tracker.tracks:
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue
                indexIDs.append(int(track.track_id))
                counter.append(int(track.track_id))
                bbox = track.to_tlbr()
                color = [int(c) for c in COLORS[indexIDs[i] % len(COLORS)]]

                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (color), 3)
                cv2.putText(frame, str(track.track_id), (int(bbox[0]), int(bbox[1] - 50)), 0, 5e-3 * 150, (color), 2)
                if len(class_names) > 0:
                    class_name = class_names[0]
                    cv2.putText(frame, str(class_names[0]), (int(bbox[0]), int(bbox[1] - 20)), 0, 5e-3 * 150, (color),
                                2)

                i += 1
                # bbox_center_point(x,y)
                center = (int(((bbox[0]) + (bbox[2])) / 2), int(((bbox[1]) + (bbox[3])) / 2))
                # track_id[center]
                pts[track.track_id].append(center)
                thickness = 5
                # center point
                cv2.circle(frame, (center), 1, color, thickness)

                # draw motion path
                for j in range(1, len(pts[track.track_id])):
                    if pts[track.track_id][j - 1] is None or pts[track.track_id][j] is None:
                        continue
                    thickness = int(np.sqrt(64 / float(j + 1)) * 2)
                    cv2.line(frame, (pts[track.track_id][j - 1]), (pts[track.track_id][j]), (color), thickness)

            count = len(set(counter))

            if writeVideo_flag:
                # save a frame
                out.write(frame)
                frame_index = frame_index + 1
                list_file.write(str(frame_index) + ' ')
                if len(boxs) != 0:
                    for i in range(0, len(boxs)):
                        list_file.write(
                            str(boxs[i][0]) + ' ' + str(boxs[i][1]) + ' ' + str(boxs[i][2]) + ' ' + str(
                                boxs[i][3]) + ' ')
                list_file.write('\n')
            fps = (fps + (1. / (time.time() - t1))) / 2
            # print(set(counter))

            # Press Q to stop!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        print(" ")
        print("[Finish]")
        end = time.time()

        if len(pts[track.track_id]) != None:
            print(video_full_path + ": " + str(count) + " " + str(class_name) + ' Found')

        else:
            print("[No Found]")

        video_capture.release()

        if writeVideo_flag:
            out.release()
            list_file.close()
        cv2.destroyAllWindows()


def test():
    sort = Sort(model_path='./model_data/yolo.h5', anchors_path='./model_data/yolo_anchors.txt',
                classes_path='./model_data/coco_classes.txt', model_filename='./model_data/market1501.pb',
                model_type='car', video_path='./test_video/test1.mp4',
                result_path='./result')
    sort.main()
