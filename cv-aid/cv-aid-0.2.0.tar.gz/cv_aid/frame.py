# pydoctor --project-base-dir=. --make-html --docformat=restructuredtext cv_aid/
# pylint: disable=C0103
__docformat__ = "restructuredtext en"

import os
import cv2
import numpy as np

from cv_aid import utils
from cv_aid.haarcascades import Haarcascades
from cv_aid._dlib import Dlib

_dlib = Dlib()


class Frame:  # pylint: disable=too-many-public-methods
    """A class to represent a frame of video."""

    def __init__(self, frame):
        """Initialize a Frame object.

        :param frame: The frame to be represented.
        :type frame: numpy.ndarray
        """
        self.frame = frame
        self.original_frame = frame.copy()
        self._haarcascades = None
        self._dlib = None

    @classmethod
    def load(cls, path) -> "Frame":
        """Load a frame from a file.

        Args:
          path(str): Path to the file.

        Returns:

        """
        return cls(cv2.imread(str(path)))

    @property
    def shape(self) -> tuple:
        """Get the shape of the frame."""
        return self.frame.shape

    @property
    def width(self) -> int:
        """Get the width of the frame."""
        return self.shape[1]

    @property
    def height(self) -> int:
        """Get the height of the frame."""
        return self.shape[0]

    @property
    def size(self) -> int:
        """Get the size of the frame."""
        return self.shape[:2]

    @property
    def channels(self) -> int:
        """Get the number of channels in the frame."""
        return self.shape[2]

    def to_bytes(self) -> bytes:
        """Convert the frame to bytes.

        :return: The resulting bytes.

        Args:

        Returns:

        """
        return self.frame.tobytes()

    def gray(self) -> "Frame":
        """Convert the frame to grayscale.

        :return: The resulting frame.

        Args:

        Returns:

        """
        return Frame(utils.gray(self.frame))

    def resize(self, width=None, height=None, inter=cv2.INTER_AREA) -> "Frame":
        """Resize the frame.

        Args:
          width(int, optional): The new width. (Default value = None)
          height(int, optional): The new height. (Default value = None)
          inter(inter: inter: int, optional): The interpolation method. (Default value = cv2.INTER_AREA)

        Returns:
          The resulting frame.

        """
        return Frame(utils.resize(self.frame, width, height, inter))

    def rotate(self, angle, center=None, scale=1.0, same_dim=True) -> "Frame":
        """Rotate the frame.

        Args:
          angle(float): The angle to rotate the frame by.
          center(tuple, optional): The center of rotation. (Default value = None)
          scale(float, optional): The scale to apply. (Default value = 1.0)
          same_dim: Default value = True)

        Returns:
          The resulting frame.

        """
        return Frame(utils.rotate(self.frame, angle, center, scale, same_dim))

    def flip(self, flip_code) -> "Frame":
        """Flip the frame.

        Args:
          flip_code(int): The code for the flip.

        Returns:
          The resulting frame.

        """
        return Frame(utils.flip(self.frame, flip_code))

    def crop(self, x, y, width, height) -> "Frame":  # pylint: disable=invalid-name
        """Crop the frame.

        Args:
          x(int): The x coordinate of the top left corner.
          y(int): The y coordinate of the top left corner.
          width(int): The width of the crop.
          height(int): The height of the crop.

        Returns:
          The resulting frame.

        """
        return Frame(utils.crop(self.frame, x, y, width, height))

    def crop_to_size(self, width, height) -> "Frame":
        """Crop the frame to a specific size.

        Args:
          width(int): The width of the frame.
          height(int): The height of the frame.

        Returns:
          The resulting frame.

        """
        return self.crop(0, 0, width, height)

    def crop_to_ratio(self, ratio) -> "Frame":
        """Crop the frame to a specific ratio.

        Args:
          ratio(float): The ratio to crop to.

        Returns:
          The resulting frame.

        """
        return self.crop_to_size(int(self.width / ratio), int(self.height / ratio))

    def crop_to_ratio_width(self, ratio) -> "Frame":
        """Crop the frame to a specific ratio.

        Args:
          ratio(float): The ratio to crop to.

        Returns:
          The resulting frame.

        """
        return self.crop_to_size(int(self.width / ratio), self.height)

    def crop_to_ratio_height(self, ratio) -> "Frame":
        """Crop the frame to a specific ratio.

        Args:
          ratio(float): The ratio to crop to.

        Returns:
          The resulting frame.

        """
        return self.crop_to_size(self.width, int(self.height / ratio))

    def blur(self, ksize=5) -> "Frame":
        """Blur the frame.

        Args:
          ksize(int, optional): The kernel size. (Default value = 5)

        Returns:
          The resulting frame.

        """
        return Frame(utils.blur(self.frame, ksize))

    def canny(self, threshold1, threshold2) -> "Frame":
        """Apply the Canny edge detector.

        Args:
          threshold1(int): The first threshold.
          threshold2(int): The second threshold.

        Returns:
          The resulting frame.

        """
        return Frame(utils.canny(self.frame, threshold1, threshold2))

    def line(
        self, start, end, color=(0, 255, 0), thickness=1, line_type=cv2.LINE_8
    ) -> "Frame":
        """Draw a line on the frame.

        Args:
          start(tuple): The start of the line.
          end(tuple): The end of the line.
          color(tuple, optional): The color of the line. (Default value = (0)
          thickness(int, optional): The thickness of the line. (Default value = 1)
          line_type(int, optional): The type of the line. (Default value = cv2.LINE_8)
          255: param 0):
          0):

        Returns:
          The resulting frame.

        """
        return Frame(utils.line(self.frame, start, end, color, thickness, line_type))

    def circle(
        self, center, radius, color=(0, 255, 0), thickness=1, line_type=cv2.LINE_8
    ) -> "Frame":
        """Draw a circle on the frame.

        Args:
          center(tuple): The center of the circle.
          radius(int): The radius of the circle.
          color(tuple, optional): The color of the circle. (Default value = (0)
          thickness(int, optional): The thickness of the circle. (Default value = 1)
          line_type(int, optional): The type of the circle. (Default value = cv2.LINE_8)

        Returns:
          The resulting frame.

        """
        return Frame(
            utils.circle(self.frame, center, radius, color, thickness, line_type)
        )

    def box(
        self,
        x,
        y,
        width,
        height,
        color,
        thickness=1,
        line_type=cv2.LINE_8,  # pylint: disable=invalid-name
        is_max=False,
    ) -> "Frame":
        """Draw a box on the frame.

        Args:
          x(int): The x coordinate of the top left corner.
          y(int): The y coordinate of the top left corner.
          width(int): The width of the box.
          height(int): The height of the box.
          color(tuple): The color of the box.
          thickness(int, optional): The thickness of the box. (Default value = 1)
          line_type(int, optional): The type of the box. (Default value = cv2.LINE_8)
          # pylint: disable:  (Default value = invalid-nameis_max=False)

        Returns:
          The resulting frame.

        """
        return Frame(
            utils.box(
                self.frame,
                x,
                y,
                width,
                height,
                color,
                thickness,
                line_type,
                is_max=is_max,
            )
        )

    def lines(self, points, color, thickness=1, line_type=cv2.LINE_8) -> "Frame":
        """Draw lines on the frame.

        Args:
          points(List[Tuple[int, int]]): The points to draw.
          color(tuple): The color of the lines.
          thickness(int, optional): The thickness of the lines. (Default value = 1)
          line_type(int, optional): The type of the lines. (Default value = cv2.LINE_8)

        Returns:
          The resulting frame.

        """
        return Frame(
            utils.lines(
                self.frame,
                points,
                color=color,
                thickness=thickness,
                line_type=line_type,
            )
        )

    def boxes(
        self, boxes, color, thickness=1, line_type=cv2.LINE_8, is_max=False
    ) -> "Frame":
        """Draw boxes on the frame.

        Args:
          boxes(List[Tuple[int, int, int, int]]): The boxes to draw.
          color(tuple): The color of the boxes.
          thickness(int, optional): The thickness of the boxes. (Default value = 1)
          line_type(int, optional): The type of the boxes. (Default value = cv2.LINE_8)
          is_max: Default value = False)

        Returns:
          The resulting frame.

        """
        return Frame(
            utils.boxes(
                self.frame,
                boxes,
                color=color,
                thickness=thickness,
                line_type=line_type,
                is_max=is_max,
            )
        )

    def text(
        self,
        text,
        position,
        font_face=cv2.FONT_HERSHEY_SIMPLEX,
        font_scale=1.0,
        color=(0, 255, 0),
        thickness=1,
    ) -> "Frame":
        """Draw text on the frame.

        Args:
          text(str): The text to draw.
          position(tuple): The position of the text.
          color(tuple, optional): The color of the text. (Default value = (0)
          font_face(int, optional): The font face of the text. (Default value = cv2.FONT_HERSHEY_SIMPLEX)
          font_scale(float, optional): The font scale of the text. (Default value = 1.0)
          thickness(int, optional): The thickness of the text. (Default value = 1)
          255: param 0):
          0):

        Returns:
          The resulting frame.

        """
        return Frame(
            utils.text(
                self.frame,
                text,
                *position,
                font_face,
                font_scale,
                color,
                thickness,
            )
        )

    def __add__(self, other) -> "Frame":
        """Add two frames together.

        :param other: The other frame to be added.
        :type other: Frame
        :return: The resulting frame.
        """
        return Frame(self.frame + other.frame)

    def __sub__(self, other) -> "Frame":
        """Subtract two frames.

        :param other: The other frame to be subtracted.
        :type other: Frame
        :return: The resulting frame.
        """
        return Frame(self.frame - other.frame)

    def __mul__(self, other) -> "Frame":
        """Multiply two frames.

        :param other: The other frame to be multiplied.
        :type other: Frame
        :return: The resulting frame.
        """
        return Frame(self.frame * other.frame)

    def __truediv__(self, other) -> "Frame":
        """Divide two frames.

        :param other: The other frame to be divided.
        :type other: Frame
        :return: The resulting frame.
        """
        return Frame(self.frame / other.frame)

    def abs(self) -> "Frame":
        """Take the absolute value of the frame.

        :return: The resulting frame.

        Args:

        Returns:

        """
        return Frame(np.abs(self.frame))

    def show(self, title="Frame") -> None:
        """Show the frame.

        Args:
          title(str, optional): The title of the frame. (Default value = "Frame")

        Returns:

        """
        cv2.imshow(title, self.frame)

    def save(self, path, name):
        """Save the frame.

        Args:
          path(str): The path to save the frame.
          name(str): The name of the frame.

        Returns:

        """
        cv2.imwrite(os.path.join(path, name), self.frame)

    def __repr__(self) -> str:
        """Get the string representation of the frame.

        :return: The string representation of the frame.
        """
        return f"Frame({self.frame.shape})"

    @property
    def haarcascades(self):
        """Provides access to the haarcascades."""
        # Create the haarcascades class if it doesn't exist
        if not hasattr(self, "_haarcascades") or getattr(self, "_haarcascades") is None:
            self._haarcascades = Haarcascades()
        return self._haarcascades

    @property
    def dlib(self):
        """Provides access to the dlib."""
        # Create the dlib class if it doesn't exist
        if not hasattr(self, "_dlib") or getattr(self, "_dlib") is None:
            self._dlib = _dlib
        return self._dlib
