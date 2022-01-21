"""
FPS Library to display Frame Per Seconds

Author: Roshaan Mehmood
"""
import time
import cv2


class FPS:
    """
    Helps in finding Frames Per Second and display on an OpenCV Image
    """

    def __init__(self):
        self.pTime = time.time()

    def showFPS(self, img=None, textPos=(20, 50), textColor=(255, 255, 255), textScale=3, textThick=3):
        """
        Update the frame rate.

        :param img: Image to display on, can be left blank if only fps value required
        :param textPos: Position of the FPS on the image
        :param textColor: Color of the FPS Value displayed
        :param textScale: Scale of the FPS Value displayed
        :param textThick: Thickness of the FPS Value displayed
        :return: Image with FPS Value
        """
        cTime = time.time()
        try:
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            if img is None:
                return fps
            else:
                cv2.putText(img, f'FPS: {int(fps)}', textPos, cv2.FONT_HERSHEY_PLAIN,
                            textScale, textColor, textThick)
                return fps, img
        except:
            return 0


def main():
    # """
    # Without Webcam
    # """
    # fpsReader = FPS()
    # while True:
    #     time.sleep(0.025)  # add delay to get 40 Frames per second
    #     fps = fpsReader.showFPS()
    #     print(fps)

    """
    With Webcam
    """
    FPSReader = FPS()
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        fps, img = FPSReader.showFPS(img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()