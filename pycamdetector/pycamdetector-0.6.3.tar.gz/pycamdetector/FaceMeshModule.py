"""
Face Mesh Module

Author: Roshaan Mehmood
"""

import cv2
import mediapipe as mp
import math


class FaceMeshDetector:
    """
    Face Mesh Detector to find 468 Landmarks using the mediapipe library.
    Helps acquire the landmark points in pixel format
    """

    def __init__(self, staticMode=False, maxFaces=2, minDetConf=0.5, minTrackConf=0.5,
                 lineThick=1, circleRadius=2):
        """
        :param staticMode: In static mode, detection is done on each image: slower
        :param maxFaces: Maximum number of faces to detect
        :param minDetConf: Minimum Detection Confidence Threshold
        :param minTrackConf: Minimum Tracking Confidence Threshold
        :param lineThick: Thickness of the mesh connection lines
        :param circleRadius: Radius of the circle of Face Mesh
        """
        self.staticMode = staticMode
        self.maxFaces = maxFaces
        self.minDetConf = minDetConf
        self.minTrackConf = minTrackConf
        self.lineThick = lineThick
        self.circleRadius = circleRadius

        self.mpDraw = mp.solutions.drawing_utils
        self.mpFaceMesh = mp.solutions.face_mesh
        self.faceMesh = self.mpFaceMesh.FaceMesh(static_image_mode=self.staticMode,
                                                 max_num_faces=self.maxFaces,
                                                 min_detection_confidence=self.minDetConf,
                                                 min_tracking_confidence=self.minTrackConf)
        self.drawSpec = self.mpDraw.DrawingSpec(thickness=lineThick, circle_radius=circleRadius)

    def findFaceMesh(self, img, drawConns=True):
        """
        Finds face landmarks in BGR Image.

        :param img: Image to find the face landmarks in.
        :param drawConns: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        self.imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.faceMesh.process(self.imgRGB)
        faces = []
        if self.results.multi_face_landmarks:
            for faceLms in self.results.multi_face_landmarks:
                if drawConns:
                    self.mpDraw.draw_landmarks(img, faceLms, self.mpFaceMesh.FACEMESH_CONTOURS,
                                               self.drawSpec, self.drawSpec)
                face = []
                for id, lm in enumerate(faceLms.landmark):
                    ih, iw, ic = img.shape
                    x, y = int(lm.x * iw), int(lm.y * ih)
                    face.append([x, y])
                faces.append(face)
        return img, faces

    def findDistance(self, p1, p2, img=None):
        """
        Find the distance between two landmarks based on their
        index numbers.

        :param p1: Point1
        :param p2: Point2
        :param img: Image to draw on.
        :return: Distance between the points
                 Image with output drawn
                 Line information
        """

        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 8, (255, 0, 255), cv2.FILLED)
            return length,info, img
        else:
            return length, info


def main():
    cap = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces=2)
    while True:
        success, img = cap.read()
        img, faces = detector.findFaceMesh(img)
        if faces:
            print(faces[0])
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
