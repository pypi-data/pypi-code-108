"""
Face Detection Module

Author: Roshaan Mehmood
"""
import cv2
import mediapipe as mp


class FaceDetector:
    """
        Find faces in realtime using the light weight model provided in the mediapipe
        library.
    """
    def __init__(self, minDetConf=0.5):
        """
            :param minDetConf: Minimum Detection Confidence Threshold
        """
        self.minDetConf = minDetConf
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(self.minDetConf)

    def findFaces(self, img, drawRect=True, showPerc=True, textColor=(255, 255, 255),
                  rectColor=(255, 255, 255), rectThick=1, corLen=30, corColor=(255, 0, 255), corThick=2):
        """
        Finds faces to detect in a BGR image.

        :param img: Image to find the faces in.
        :param drawRect: Flag to draw the rectangle around the faces detected.
        :param showPerc: Flag to display accuracy percentage.
        :param textColor: Color of the text of accuracy percentage.
        :param rectColor: Color of the rectangle.
        :param rectThick: Thickness of the rectangle.
        :param corLen: Length of the corner lines of rectangle.
        :param corColor: Color of the rectangle corners.
        :param corThick: Thickness of the rectangle corners.
        :return: Image with or without drawings.
                 Bounding Box list.
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_detection.process(imgRGB)
        bboxs = []

        if self.results.detections:
            for detection in self.results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                bboxs.append([bbox, detection.score])
                if drawRect:
                    img = self.fancyDraw(img, bbox, rectColor=rectColor, corColor=corColor,
                                         t=corThick, rt=rectThick, l=corLen)
                if showPerc:
                    cv2.putText(img, f' {int(detection.score[0] * 100)}%',
                                (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, textColor, 2)
        return img, bboxs

    def fancyDraw(self, img, bbox, l=30, t=2, rt=1, rectColor=(255, 255, 255), corColor=(255, 0, 255)):
        x, y, w, h = bbox
        x1, y1 = x + w, y + h
        cv2.rectangle(img, bbox, rectColor, rt)
        # Top left x,y
        cv2.line(img, (x, y), (x + l, y), corColor, t)
        cv2.line(img, (x, y), (x, y + l), corColor, t)

        # Top right x1,y
        cv2.line(img, (x1, y), (x1 - l, y), corColor, t)
        cv2.line(img, (x1, y), (x1, y + l), corColor, t)

        # Bottom left x,y1
        cv2.line(img, (x, y1), (x + l, y1), corColor, t)
        cv2.line(img, (x, y1), (x, y1 - l), corColor, t)

        # Bottom Right x1,y1
        cv2.line(img, (x1, y1), (x1 - l, y1), corColor, t)
        cv2.line(img, (x1, y1), (x1, y1 - l), corColor, t)

        return img


def main():
    cap = cv2.VideoCapture(0)
    detector = FaceDetector(minDetConf=0.85)
    while True:
        success, img = cap.read()
        img = cv2.cv2.flip(img, 1)
        img, bboxs = detector.findFaces(img, showPerc=False)
        print(bboxs)
        cv2.imshow('Image', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()