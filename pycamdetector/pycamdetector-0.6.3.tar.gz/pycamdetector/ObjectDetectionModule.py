"""
Object Detection Module for detecting objects

Author: Roshaan Mehmood
"""
import cv2
import numpy as np


class ObjectDetector:
    def __init__(self, weightpath, configpath, labelsPath):
        self.weightpath = weightpath
        self.configpath = configpath
        self.net = cv2.dnn_DetectionModel(self.weightpath, self.configpath)
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)
        self.labelsPath = labelsPath
        if self.labelsPath:
            label_file = open(self.labelsPath, 'rt')
            self.classLabels = []
            for line in label_file:
                stripped_line = line.strip()
                self.classLabels.append(stripped_line)
            label_file.close()
        else:
            print("No Labels Found")

    def DetectObject(self, img, thres=0.45, nms_threshold=0.2, color=(0, 255, 0)):
        img = cv2.flip(img, 1)
        classIds, confs, bbox = self.net.detect(img, confThreshold=0.5)
        bbox = list(bbox)
        confs = list(np.array(confs).reshape(1, -1)[0])
        confs = list(map(float, confs))

        indices = cv2.dnn.NMSBoxes(bbox, confs, thres, nms_threshold)

        for i in indices:
            i = i[0]
            box = bbox[i]
            x, y, w, h = box[0], box[1], box[2], box[3]
            cv2.rectangle(img, (x, y), (x + w, h + y), color=color, thickness=2)
            cv2.putText(img, self.classLabels[classIds[i][0] - 1].upper(), (box[0] + 10, box[1] + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return img, indices

    # if len(classIds) != 0:
    #     for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
    #         cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
    #         cv2.putText(img, classLabels[classId - 1].upper(), (box[0] + 10, box[1] + 30),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    #         cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    configpath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightpath = 'frozen_inference_graph.pb'
    labelsPath = 'coco.names'

    objectdetector = ObjectDetector(weightpath, configpath, labelsPath)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img, indices = objectdetector.DetectObject(img)
        print(indices)
        cv2.imshow("Output", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
