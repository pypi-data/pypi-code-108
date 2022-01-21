# pylint: disable=C0103
__docformat__ = "restructuredtext en"

from threading import Thread

import cv2

from cv_aid import Frame


class VideoStream:
    """A class for streaming video from a camera.

    Args:
      src: The source of the video stream.

    Returns:

    """

    def __init__(self, src, width=None, height=None, on_frame=None):
        """
        Initialize the video stream and read the first frame from the stream.

        :param src: The source of the video stream.
        :param width: The width of the frame.
        :type width: int
        :param height: The height of the frame.
        :type height: int
        """
        self.src = src
        self.stopped = False  # Indicates if the video stream is stopped.
        self.paused = False  # Indicates if the video stream is paused.
        self.stream = cv2.VideoCapture(src)  # The video stream.
        if width is not None and height is not None:
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.on_frame = on_frame
        self.frame = self.read()  # The current frame.
        self.thread = Thread(
            target=self.update, args=()
        )  # The thread that reads the video stream.
        # self.thread.daemon = True  # Make the thread a daemon thread.
        self.is_window_open = False  # Indicates if a window is open.

    def read(self) -> Frame:
        """Read a frame from the video stream and return it."""
        success, frame = self.stream.read()
        if not success:
            self.stop()
        frame = Frame(frame)
        if self.on_frame is not None:
            frame = self.on_frame(frame)
            if not isinstance(frame, Frame):
                frame = Frame(frame)
        return frame

    def start(self):
        """Start the video stream."""
        self.thread.start()
        return self

    def update(self):
        """ """
        while True:
            if self.stopped:
                return
            if self.paused:
                continue
            self.frame = self.read()

    def pause(self):
        """Pause the video stream."""
        self.paused = True

    def resume(self):
        """Resume the video stream."""
        self.paused = False

    def stop(self):
        """Stop the video stream."""
        self.stopped = True
        self.kill()
        return self

    def __del__(self):
        self.kill()

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill()

    def kill(self):
        """Kill the video stream."""
        self.stream.release()
        self.thread.join()
        self.close_windows()

    def start_window(self, title=None):
        """Start a window to display the video stream.

        Args:
          title(str, optional): The title of the window. (Default value = None)

        Returns:

        """
        self.is_window_open = True
        if title is None:
            title = f"Streaming '{self.src}' Frames"
        while True:
            self.read().show(title)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.close_windows()
                break

    def close_windows(self):
        """ """
        cv2.destroyAllWindows()
        self.is_window_open = False
