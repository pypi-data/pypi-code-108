# pylint: disable=C0103

__docformat__ = "restructuredtext en"

import numpy as np
import dlib


class Dlib:
    """Provides a class for loading and using dlib models."""

    def __init__(self, landmark_predictor_path="shape_predictor_68_face_landmarks.dat"):
        """Initializes Dlib.

        :param face_shape_path: path to face shape predictor
        :type face_shape_path: str
        """

        self.face_detector = dlib.get_frontal_face_detector()
        """Face detector."""

        self.landmark_predictor = dlib.shape_predictor(landmark_predictor_path)
        """Face landmark predictor."""

    def detect_faces(self, image: np.ndarray, **kwargs):
        """Detects faces in an image.

        Args:
          image: image to detect faces in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing faces

        """

        # Get faces and scores
        faces_ = self.face_detector(image, **kwargs)
        return faces_

    def detect_landmarks(self, image: np.ndarray, rectangle: tuple, **kwargs):
        """Detects landmarks in an image.

        Args:
          image: image to detect landmarks in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          rectangle: tuple:
          **kwargs:

        Returns:
          list of rectangles containing landmarks

        """

        # Get landmarks and scores
        landmarks_ = self.landmark_predictor(image, rectangle, **kwargs)
        return landmarks_

    @classmethod
    def convert_and_trim_bb(cls, image, rectangle):
        """Converts a bounding box to a normal box with respect to the image.

        Args:
          image: image to convert and trim
          rect: bounding box to convert and trim
          rectangle:

        Returns:
          trimmed image

        """
        # extract the starting and ending (x, y)-coordinates of the
        # bounding box
        startX = rectangle.left()
        startY = rectangle.top()
        endX = rectangle.right()
        endY = rectangle.bottom()
        # ensure the bounding box coordinates fall within the spatial
        # dimensions of the image
        startX = max(0, startX)
        startY = max(0, startY)
        endX = min(endX, image.shape[1])
        endY = min(endY, image.shape[0])
        # compute the width and height of the bounding box
        w = endX - startX
        h = endY - startY
        # return our bounding box coordinates
        return (int(startX), int(startY), int(w), int(h))

    @classmethod
    def download_shape_predictor(cls, path="./"):
        """Downloads shape predictor.

        Args:
          path(str, optional): path to download to (Default value = "./")

        Returns:

        """
        return cls.download_and_extract(
            url="http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2",
            path=path,
        )

    @classmethod
    def download_face_recognition_model_v1(cls, path="./"):
        """Downloads face recognition model v1.

        Args:
          path(str, optional): path to download to (Default value = "./")

        Returns:

        """
        return cls.download_and_extract(
            url="http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2",
            path=path,
        )

    @classmethod
    def download_landmark_detector(cls, path="./"):
        """Downloads landmark detector.

        Args:
          path(str, optional): path to download to (Default value = "./")

        Returns:

        """
        return cls.download_and_extract(
            url="http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
            path=path,
        )

    @classmethod
    def download_and_extract(cls, url, path="./"):
        """Downloads and extracts shape predictor.

        Args:
          url: url to download file from
          path: path to extract file to (Default value = "./")

        Returns:
          path to downloaded file

        """
        from tqdm import tqdm
        import bz2
        import os
        import requests

        r = requests.get(url, stream=True)
        # Get file name from url
        file_name = r.url.split("/")[-1]
        out_file = os.path.join(path, file_name.split(".")[0] + ".dat")
        file_size = int(r.headers["Content-Length"])
        with open(file_name, "wb") as file, tqdm(
            desc=f"Downloading '{file_name}'",
            total=file_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in r.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        # Extract file
        with bz2.open(file_name, "rb") as f_in, open(out_file, "wb") as f_out:
            for chunk in tqdm(
                f_in,
                total=os.path.getsize(path),
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Extracting file '{file_name}'",
            ):
                f_out.write(chunk)
        # Remove compressed file
        os.remove(file_name)
        return out_file
