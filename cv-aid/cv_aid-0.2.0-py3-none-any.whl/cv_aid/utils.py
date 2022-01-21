# pylint: disable=C0103
__docformat__ = "restructuredtext en"

import base64
import itertools
from pathlib import Path
from typing import Generator, Iterable

import cv2
import filetype
import numpy as np
from deepstack_sdk import ServerConfig


def find_images(path: Path) -> Generator:
    """Finds all images in a directory.

    Args:
      path(Path): path to the directory to search in
      path: Path:

    Returns:
      generator of all images in the directory

    """
    for file in path.iterdir():
        if file.is_dir():
            continue
        if filetype.is_image(file):
            yield file


def find_videos(path: Path) -> Generator:
    """Finds all videos in a directory.

    Args:
      path(Path): path to the directory to search in
      path: Path:

    Returns:
      generator of all videos in the directory

    """
    for file in path.iterdir():
        if file.is_dir():
            continue
        if filetype.is_video(file):
            yield file


def find_fonts(path: Path) -> Generator:
    """Finds all fonts in a directory.

    Args:
      path(Path): path to the directory to search in
      path: Path:

    Returns:
      generator of all fonts in the directory

    """
    for file in path.iterdir():
        if file.is_dir():
            continue
        if filetype.is_font(file):
            yield file


def rotate(img: np.ndarray, angle, center=None, scale=1.0, same_dim=True) -> np.ndarray:
    """Rotates an image.

    Args:
      img(np.ndarray): image to rotate
      angle(int): angle to rotate the image by
      center(tuple, optional): center of the image to rotate around (Default value = None)
      scale(float, optional): scale of the image (Default value = 1.0)
      same_dim(bool, optional): if True, the image will be resized to the same dimensions as the original (Default value = True)
      img: np.ndarray:

    Returns:
      rotated image

    """

    if not same_dim:
        return cv2.rotate(img, angle)
    # get the dimensions of the image
    (height, width) = img.shape[:2]

    # if the center is None, initialize it as the center of the image
    if center is None:
        center = (width / 2, height / 2)

    # the rotation
    rota_matrix = cv2.getRotationMatrix2D(center, angle, scale)
    rotated_img = cv2.warpAffine(img, rota_matrix, (width, height))

    # return the rotated image
    return rotated_img


def resize(img: np.ndarray, width, height, inter=cv2.INTER_AREA) -> np.ndarray:
    """Resizes an image.

    Args:
      img(np.ndarray): image to resize
      width(int): width of the resized image
      height(int): height of the resized image
      inter(inter: int, optional): interpolation method (Default value = cv2.INTER_AREA)
      img: np.ndarray:

    Returns:
      resized image

    """
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        ratio = height / float(height)
        dim = (int(img.shape[1] * ratio), height)
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        ratio = width / float(width)
        dim = (width, int(height * ratio))

    # resize the image
    resized = cv2.resize(img, dim, interpolation=inter)

    return resized


def concatenate(image1: np.ndarray, image2: np.ndarray, axis=1) -> np.ndarray:
    """Concatenates two images.

    Args:
      image1(np.ndarray): first image to concatenate
      image2(np.ndarray): second image to concatenate
      axis(int, optional): axis to concatenate the images on (Default value = 1)
      image1: np.ndarray:
      image2: np.ndarray:

    Returns:
      concatenated image

    """
    return np.concatenate((image1, image2), axis=axis)


def batch(iterable: Iterable, length: int) -> Generator:
    """Batches an iterable.

    Args:
      iterable(Iterable): iterable to batch
      n(int): number of items to batch
      iterable: Iterable:
      length: int:

    Returns:
      generator of batches

    """
    iterator = iter(iterable)
    while item := list(itertools.islice(iterator, length)):
        yield item


def is_type(obj, type_name):
    """Checks if an object is of a certain type.

    Args:
      obj(object): object to check
      type_name(str): name of the type to check

    Returns:
      True if the object is of the type, False otherwise

    """
    return type(obj).__name__ == type_name


def verify_frame_type(func):
    """Verifies that the frame type is correct.

    Args:
      func(function): function to decorate

    Returns:
      decorated function

    """

    def wrapper(self, frame, *args, **kwargs):
        """

        Args:
          frame:
          *args:
          **kwargs:

        Returns:

        """
        if is_type(frame, "Frame"):
            raise TypeError("The frame must be a Frame object")
        return func(self, frame, *args, **kwargs)

    return wrapper


def copy_frame(func):
    """Copies the frame before applying the function.

    Args:
      func(function): function to decorate

    Returns:
      decorated function

    """

    def wrapper(*args, **kwargs):
        """

        Args:
          *args:
          **kwargs:

        Returns:

        """
        frame = args[0]
        new_frame = type(frame)(frame.frame.copy())
        return func(new_frame, *args[1:], **kwargs)

    return wrapper


def verify_deepstack_config(func):
    """Verifies that the DeepStack config is correct.

    Args:
      func(function): function to decorate

    Returns:
      decorated function

    """

    def wrapper(self, *args, **kwargs):
        """

        Args:
          *args:
          **kwargs:

        Returns:

        """
        server_config = kwargs.get("config")
        if server_config is None:
            try:
                server_config = args[1]
            except KeyError:
                raise ValueError(
                    "The server_config must be a ServerConfig object"
                ) from None

        if server_config is None or not isinstance(server_config, ServerConfig):
            raise ValueError("The server_config must be a ServerConfig object")
        if self.server_config.server_url is None:
            raise ValueError("The server_config must have a server_url")

        return func(self, *args, **kwargs)

    return wrapper


class TemplateResponse:
    """TemplateResponse class."""

    def __init__(self, frame, loc, template):
        """
        Initializes the TemplateResponse class.

        :param frame: frame to apply the template to
        :type frame: np.ndarray
        :param loc: location of the template
        :type loc: tuple
        :param template: template to apply
        :type template: np.ndarray
        """
        self.frame = frame
        self.loc = loc
        self.template = template
        self.width = template.shape[1]
        self.height = template.shape[0]
        self.orig = frame.copy()

    def draw_boxes(self) -> "TemplateResponse":
        """Draws the boxes on the frame.

        :return: The resulting TemplateResponse object

        Args:

        Returns:

        """
        for x, y, width, height, color in self.boxes():
            self.frame = box(self.frame, x, y, width, height, color)
        return self

    def __len__(self):
        return len(self.boxes())

    def __repr__(self):
        return f"TemplateResponse({self.frame})"

    def boxes(self, color=(0, 255, 0)) -> Generator:
        """Returns the boxes of the template.

        Args:
          color(tuple, optional): color of the boxes (Default value = (0)
          255:
          0):

        Returns:
          generator of boxes

        """
        # for x, y in self.loc:
        # yield x, y, self.w, self.h, color
        for point in zip(*self.loc[::-1]):
            yield [
                point[0],
                point[1],
                point[0] + self.width,
                point[1] + self.height,
                color,
            ]


# OpenCV functions


def gray(frame: np.ndarray) -> np.ndarray:
    """Converts a color image to grayscale.

    Args:
      frame(np.ndarray): image to convert to grayscale
      frame: np.ndarray:

    Returns:
      grayscale image

    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def crop(frame: np.ndarray, x, y, width, height) -> np.ndarray:
    """Crops an image.

    Args:
      frame(np.ndarray): image to crop
      x(int): x coordinate of the top left corner
      y(int): y coordinate of the top left corner
      w(int): width of the crop
      h(int): height of the crop
      frame: np.ndarray:
      width:
      height:

    Returns:
      cropped image

    """
    return frame[y : y + height, x : x + width]


def blur(frame: np.ndarray, ksize=(5, 5)) -> np.ndarray:
    """Blurs an image.

    Args:
      frame(np.ndarray): image to blur
      ksize(tuple, optional): size of the kernel (Default value = (5)
      frame: np.ndarray:
      5):

    Returns:
      blurred image

    """
    return cv2.blur(frame, ksize=ksize)


def flip(frame: np.ndarray, flip_code=1) -> np.ndarray:
    """Flips an image.

    Args:
      frame(np.ndarray): image to flip
      flip_code(int, optional): code for flipping the image (Default value = 1)
      frame: np.ndarray:

    Returns:
      flipped image

    """
    return cv2.flip(frame, flip_code)


def line(
    frame: np.ndarray,
    start: tuple,
    end: tuple,
    color=(0, 255, 0),
    thickness=2,
    line_type=cv2.LINE_8,
) -> np.ndarray:
    """Draws a line on an image.

    Args:
      frame(np.ndarray): image to draw the line on
      start(tuple): start point of the line
      end(tuple): end point of the line
      color(tuple, optional): color of the line (Default value = (0)
      thickness(int, optional): thickness of the line (Default value = 2)
      line_type(int, optional): type of the line (Default value = cv2.LINE_8)
      frame: np.ndarray:
      start: tuple:
      end: tuple:
      255:
      0):

    Returns:
      image with the line

    """
    return cv2.line(frame, start, end, color, thickness, line_type)


def lines(frame, points: list, **kwargs):
    """Draws multiple lines on an image.

    Args:
      frame(np.ndarray): image to draw the lines on
      points(list): list of points to draw lines between
      kwargs(dict): keyword arguments for line
      points: list:
      **kwargs:

    Returns:
      image with the lines

    """
    for i in range(len(points) - 1):
        frame = line(frame, points[i][0], points[i][1], **kwargs)
    return frame


def circle(
    frame: np.ndarray,
    center: tuple,
    radius: int,
    color=(0, 255, 0),
    thickness=2,
    lineType=cv2.LINE_8,
) -> np.ndarray:
    """Draws a circle on an image.

    Args:
      frame(np.ndarray): image to draw the circle on
      center(tuple): center of the circle
      radius(int): radius of the circle
      color(tuple, optional): color of the circle (Default value = (0)
      thickness(int, optional): thickness of the circle (Default value = 2)
      lineType(int, optional): type of the circle (Default value = cv2.LINE_8)

    Returns:
      image with the circle

    """
    return cv2.circle(frame, center, radius, color, thickness, lineType)


def box(
    frame: np.ndarray,
    x,
    y,
    width,
    height,
    color=(0, 255, 0),
    thickness=1,
    line_type=cv2.LINE_8,
    is_max=False,  # pylint: disable=redefined-outer-name
) -> np.ndarray:
    """Draws a box on an image.

    Args:
      frame(np.ndarray): image to draw the box on
      x(int): x coordinate of the top left corner
      y(int): y coordinate of the top left corner
      w(int): width of the box
      h(int): height of the box
      color(tuple, optional): color of the box (Default value = (0)
      thickness(int, optional): thickness of the box (Default value = 1)
      line_type(int, optional): type of the box (Default value = cv2.LINE_8)
      max(bool): if True, treat the box as a max box
      frame: np.ndarray:
      width:
      height:
      255:
      0):
      is_max:  (Default value = False)
      # pylint: disable:  (Default value = redefined-outer-name)

    Returns:
      image with the box

    """
    if is_max:
        frame = cv2.rectangle(
            frame, (x, y), (width, height), color, thickness, line_type
        )
    else:
        frame = cv2.rectangle(
            frame, (x, y), (x + width, y + height), color, thickness, line_type
        )
    return frame


def boxes(frame, cords, **kwargs):
    """Draws multiple boxes on an image.

    Args:
      frame(np.ndarray): image to draw the boxes on
      cords(list): list of coordinates of the boxes
      kwargs(dict): keyword arguments for box
      **kwargs:

    Returns:
      image with the boxes

    """
    for _box in cords:
        frame = box(frame, *_box, **kwargs)
    return frame


def canny(frame: np.ndarray, threshold1=100, threshold2=200) -> np.ndarray:
    """Applies Canny edge detection to an image.

    Args:
      frame(np.ndarray): image to apply Canny edge detection to
      threshold1(int, optional): first threshold for Canny edge detection (Default value = 100)
      threshold2(int, optional): second threshold for Canny edge detection (Default value = 200)
      frame: np.ndarray:

    Returns:
      image with the Canny edge detection applied

    """
    return cv2.Canny(frame, threshold1, threshold2)


def text(
    frame: np.ndarray,
    text_: str,
    x: int,
    y: int,
    font=cv2.FONT_HERSHEY_SIMPLEX,
    scale=0.5,
    color=(0, 255, 0),
    thickness=2,
) -> np.ndarray:
    """Draws text on an image.

    Args:
      frame(np.ndarray): image to draw the text on
      text_(str): text to draw
      x(int): x coordinate of the top left corner
      y(int): y coordinate of the top left corner
      font(int, optional): font to use for the text (Default value = cv2.FONT_HERSHEY_SIMPLEX)
      scale(float, optional): scale of the text (Default value = 0.5)
      color(tuple, optional): color of the text (Default value = (0)
      thickness(int, optional): thickness of the text (Default value = 2)
      frame: np.ndarray:
      text_: str:
      x: int:
      y: int:
      255:
      0):

    Returns:
      image with the text

    """
    return cv2.putText(frame, text_, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def text_above_box(
    frame: np.ndarray,
    text_: str,
    cords: tuple,
    font=cv2.FONT_HERSHEY_SIMPLEX,
    scale=0.5,
    color=(0, 255, 0),
    thickness=2,
) -> np.ndarray:
    """Draws text above a box on an image.

    Args:
      frame(np.ndarray): image to draw the text on
      text_(str): text to draw
      cords(tuple): coordinates of the box
      font(int, optional): font to use for the text (Default value = cv2.FONT_HERSHEY_SIMPLEX)
      scale(float, optional): scale of the text (Default value = 0.5)
      color(tuple, optional): color of the text (Default value = (0)
      thickness(int, optional): thickness of the text (Default value = 2)
      frame: np.ndarray:
      text_: str:
      cords: tuple:
      255:
      0):

    Returns:
      image with the text

    """
    return text(
        frame,
        text_,
        cords[0],
        cords[1] - int(scale * 30),
        font,
        scale,
        color,
        thickness,
    )


def search(frame, template, method=cv2.TM_CCOEFF_NORMED, threshold=0.8):
    """Searches for a template in an image.

    Args:
      frame(np.ndarray): image to search for the template in
      template(np.ndarray): template to search for
      method(int, optional): method to use for template matching (Default value = cv2.TM_CCOEFF_NORMED)
      threshold(float, optional): threshold for template matching (Default value = 0.8)

    Returns:
      coordinates of the template in the image

    """
    if is_type(template, "Frame"):
        template = template.frame
    result = cv2.matchTemplate(frame, template, method)
    loc = np.where(result >= threshold)
    return TemplateResponse(frame, loc, template)


def stack(frames: list, resize_=None, cols=2) -> np.ndarray:
    """Stacks frames into a single image.

    Args:
      frames(list): frames to stack
      resize_(tuple, optional): resize the frames (Default value = None)
      cols(int, optional): number of columns in the stacked image (Default value = 2)
      frames: list:

    Returns:
      stacked frames

    """
    min_width = min([frame.shape[1] for frame in frames])
    min_height = min([frame.shape[0] for frame in frames])

    if resize_ is not None:
        min_width = resize_[0]
        min_height = resize_[1]
    # Resize each frame to the minimum width and height
    frames = [resize(frame, min_width, min_height) for frame in frames]

    # Calculate the width and height of the stack by summing the width and height of each frame
    _width = sum([frame.shape[1] for frame in frames])
    _height = sum([frame.shape[0] for frame in frames])
    if cols is not None:
        _width = min_width * cols
        rows_count = int((len(frames) / cols))
        if len(frames) % cols != 0:
            rows_count += 1
        _height = rows_count * min_height

    stacked = np.zeros((_height, _width, 3), np.uint8)

    frames_as_rows = batch(frames, cols)
    for row_index, row in enumerate(frames_as_rows):
        col_index = 0
        for col_index, frame in enumerate(row):
            x = col_index * min_width
            y = row_index * min_height
            stacked[y : y + frame.shape[0], x : x + frame.shape[1]] = frame
        if len(row) < cols:
            # Fill the remaining space with white
            x = (col_index * min_width) + (cols - len(row)) * min_width
            y = row_index * min_height

            stacked[
                y : y + min_height,
                x - (min_width * ((cols - len(row)) - 1)) : x + min_width,
            ] = 255

    return stacked


def to_bytes(frame: np.ndarray) -> bytes:
    """Converts a frame to bytes.

    Args:
      frame(np.ndarray): frame to convert
      frame: np.ndarray:

    Returns:
      bytes

    """
    return frame.tobytes()


def to_frame(bytes_: bytes) -> np.ndarray:
    """Converts bytes to a frame.

    Args:
      bytes_(bytes_: bytes): bytes to convert
      bytes_: bytes:

    Returns:
      frame

    """
    return np.frombuffer(bytes_, dtype=np.uint8)


def to_base64(bytes_: bytes) -> str:
    """Converts bytes to a base64 string.

    Args:
      bytes_(bytes_: bytes): bytes to convert
      bytes_: bytes:

    Returns:
      base64 string

    """
    return base64.b64encode(bytes_).decode("utf-8")


def from_base64(base64_: str) -> np.ndarray:
    """Converts a base64 string to bytes.

    Args:
      base64_(str): base64 string to convert
      base64_: str:

    Returns:
      np.ndarray frame

    """
    return to_frame(base64.b64decode(base64_))
