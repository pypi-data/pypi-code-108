"""
resizer for :mod:`photoResizer` application.
 
:creationdate:  06/01/2022 08:43
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: photoResizer.resizer
"""
import logging

import multiprocessing
from pathlib import Path
from typing import List, Union, Tuple

from willow import Image

logger = logging.getLogger(__name__)
__author__ = "fguerin"

FACE_CROP_RATIO = 1.6


class PhotoResizerError(Exception):
    """Base class for exceptions in this module."""

    pass


class PhotoResizer:
    """Pretty image resizer with image centering and cropping."""

    def __init__(
        self,
        input_files: List[Path],
        output_dir: Path,
        width: int,
        height: int,
        quality: int,
        image_format: str = "jpeg",
        with_face_detection: bool = False,
    ):
        """
        Initialize the PhotoResizer.

        :param input_files: List of input files to resize.
        :param output_dir: The output directory.
        :param width: The width of the output image.
        :param height: The height of the output image.
        :param quality: The quality of the output image.
        :param image_format: The output image format.
        :param with_face_detection: If True, use face detection.
        """
        self.input_files = input_files
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.quality = quality
        self.image_format = image_format
        self.with_face_detection = with_face_detection

        self.processes = multiprocessing.cpu_count()

    def resize_image(
        self,
        input_file: Path,
    ) -> Union[Path, List[Path]]:
        """
        Resize the input file and save it to the output file.

        :param input_file: The input file.
        :param with_face_detection: If True, use face detection.
        """
        logger.debug(f"PhotoResizer::resize_image() Resizing {input_file}")
        pr_image = PRImage(input_file)
        # Process images
        if self.with_face_detection:
            image = pr_image.crop_at_face(width=self.width, height=self.height)
        else:
            image = pr_image.crop_at_center(width=self.width, height=self.height)

        # Multiple images detected
        if isinstance(image, list):
            output_paths = []
            for idx, image in enumerate(image, 1):
                output_path = self.output_dir / f"{input_file.stem}-{idx:03d}.{self.image_format}"
                image.save(self.image_format, output_path)
                logger.info(f"PhotoResizer::resize_image() Saved (MULTI) {output_path}")
                output_paths.append(output_path)
            return output_paths

        # Single image detected
        output_path = self.output_dir / f"{input_file.stem}.{self.image_format}"
        image.save(self.image_format, output_path)
        logger.info(f"PhotoResizer::resize_image() Saved {output_path}")
        return output_path

    def resize_images(
        self,
        with_multiprocessing: bool = True,
        with_face_detection: bool = False,
    ) -> List[Path]:
        """
        Resize the input files.

        :param with_multiprocessing: If True, use multiprocessing.
        :param with_face_detection: If True, use face detection.
        :return: List of output files.
        """

        if with_multiprocessing:
            with multiprocessing.Pool(self.processes) as pool:
                output = pool.map(self.resize_image, self.input_files)
                pool.close()
                pool.join()
        else:
            output = list(map(self.resize_image, self.input_files))
        return output


class PRImage:
    """Resizeable image."""

    def __init__(self, path: Path):
        self.path = path
        f = path.open("rb")
        _image = Image.open(f)
        self._image = _image.auto_orient()

    @staticmethod
    def _resize(image: Image, width: int, height: int) -> Image:
        """
        Resize the image.

        :param image: The image to resize.
        :param width: The width of the output image.
        :param height: The height of the output image.
        :return: The resized image.
        """
        image_width, image_height = image.get_size()
        logger.debug(f"PRImage::_resize() Resizing {image_width} x {image_height} to {width} x {height}")
        original_ratio = image_width / image_height
        attended_ratio = width / height
        if original_ratio < attended_ratio:
            margin_top = int((image_height - image_width / attended_ratio) / 2)
            margin_bottom = image_height - margin_top
            crop = (
                0,
                margin_top,
                image_width,
                margin_bottom,
            )
            logger.debug(f"PRImage::_resize() V - Cropping image at {crop}")
        else:
            margin_left = int((image_width - image_height * attended_ratio) / 2)
            margin_right = image_width - margin_left
            crop = (
                margin_left,
                0,
                margin_right,
                image_height,
            )
            logger.debug(f"PRImage::_resize() H - Cropping image at {crop}")
        return image.crop(crop).resize((width, height))

    def crop_at_center(self, width: int, height: int) -> Image:
        assert self._image, "Image not loaded"
        assert width is not None, "Width must be provided"
        assert height is not None, "Height must be provided"
        return self._resize(self._image, width, height)

    def crop_at_face(self, width: int, height: int) -> Union[Image, List[Image]]:
        """
        Crop and resize, using optionally detect_faces from OpenCV.

        :param width: Output width
        :param height: Output height
        :return: Cropped and resized image
        """
        # Detect faces
        try:
            import cv2
        except ImportError:
            raise PhotoResizerError("OpenCV not installed. To use face detection, install OpenCV.")

        faces = self._image.detect_faces()
        if len(faces) == 0:
            raise PhotoResizerError(f"No faces detected in {self.path}")

        # Multiple faces detected
        if len(faces) == 1:
            face = faces[0]
            return self.extract_face(
                face=face,
                height=height,
                width=width,
            )

        face_images = []
        for face in reversed(faces):
            # Compute face surface
            face_surface = (face[2] - face[0]) * (face[3] - face[1])
            image_surface = self._image.get_size()[0] * self._image.get_size()[1]

            if face_surface / image_surface < 0.25:
                continue

            output = self.extract_face(
                face=face,
                height=height,
                width=width,
            )
            face_images.append(output)
        return face_images

    def extract_face(
        self,
        face: Tuple[int, int, int, int],
        height: int,
        width: int,
    ) -> Image:
        """
        Extract the face and resize it.

        :param image: Image to extract the face from
        :param face: The faces
        :param height: The height of the output image
        :param width: The width of the output image
        :return: The cropped and resized image
        """
        face_center = int((face[0] + face[2]) / 2), int((face[1] + face[3]) / 2)
        face_size = int((face[2] - face[0]) * FACE_CROP_RATIO), int((face[3] - face[1]) * FACE_CROP_RATIO)
        logger.debug(f"extract_face() Cropping face at {face_center} with size {face_size}")
        face_crop = (
            int(face_center[0] - face_size[0] / 2),
            int(face_center[1] - face_size[1] / 2),
            int(face_center[0] + face_size[0] / 2),
            int(face_center[1] + face_size[1] / 2),
        )
        logger.debug(f"extract_face() Cropping image at {face_crop}")
        image = self._image.crop(face_crop)
        return self._resize(image, width, height)
