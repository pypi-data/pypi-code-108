# pylint: disable=C0103
__docformat__ = "restructuredtext en"

import cv2
import numpy as np


class Haarcascades:
    """Class for loading and using haarcascades."""

    def __init__(self):
        """Initializes Haarcascades."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        """Cascade classifier for faces."""

        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )
        """Cascade classifier for eyes."""

        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )
        """Cascade classifier for smiles."""

        self.upper_body = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_upperbody.xml"
        )
        """Cascade classifier for upper body."""

        self.lower_body = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_lowerbody.xml"
        )
        """Cascade classifier for lower body."""

        self.full_body = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_fullbody.xml"
        )
        """Cascade classifier for full body."""

        self.profile_face = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_profileface.xml"
        )
        """Cascade classifier for profile faces."""

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
        faces_ = self.face_cascade.detectMultiScale(image, **kwargs)
        return faces_

    def detect_eyes(self, image: np.ndarray, **kwargs):
        """Detects eyes in an image.

        Args:
          image: image to detect eyes in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing eyes

        """
        # Get eyes and scores
        eyes = self.eye_cascade.detectMultiScale(image, **kwargs)
        return eyes

    def detect_smiles(self, image: np.ndarray, **kwargs):
        """Detects smiles in an image.

        Args:
          image: image to detect smiles in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing smiles

        """
        # Get smiles and scores
        smiles = self.smile_cascade.detectMultiScale(image, **kwargs)
        return smiles

    def detect_upperbody(self, image: np.ndarray, **kwargs):
        """Detects upper body in an image.

        Args:
          image: image to detect upper body in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing upper body

        """
        # Get upper body and scores
        upper_body = self.upper_body.detectMultiScale(image, **kwargs)
        return upper_body

    def detect_lowerbody(self, image: np.ndarray, **kwargs):
        """Detects lower body in an image.

        Args:
          image: image to detect lower body in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing lower body

        """
        # Get lower body and scores
        lower_body = self.lower_body.detectMultiScale(image, **kwargs)
        return lower_body

    def detect_fullbody(self, image: np.ndarray, **kwargs):
        """Detects full body in an image.

        Args:
          image: image to detect full body in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing full body

        """
        # Get full body and scores
        full_body = self.full_body.detectMultiScale(image, **kwargs)
        return full_body

    def detect_profileface(self, image: np.ndarray, **kwargs):
        """Detects profile face in an image.

        Args:
          image: image to detect profile face in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing profile face

        """
        # Get profile face and scores
        profile_face = self.profile_face.detectMultiScale(image, **kwargs)
        return profile_face

    def detect_all(self, image: np.ndarray, **kwargs):
        """Detects all objects in an image.

        Args:
          image: image to detect objects in
          kwargs: kwargs for detectMultiScale
          image: np.ndarray:
          **kwargs:

        Returns:
          list of rectangles containing objects

        """
        # Get all objects and scores
        faces_ = self.face_cascade.detectMultiScale(image, **kwargs)
        eyes = self.eye_cascade.detectMultiScale(image, **kwargs)
        smiles = self.smile_cascade.detectMultiScale(image, **kwargs)
        upper_body = self.upper_body.detectMultiScale(image, **kwargs)
        lower_body = self.lower_body.detectMultiScale(image, **kwargs)
        full_body = self.full_body.detectMultiScale(image, **kwargs)
        profile_face = self.profile_face.detectMultiScale(image, **kwargs)
        return {
            "faces": faces_,
            "eyes": eyes,
            "smiles": smiles,
            "upper_body": upper_body,
            "lower_body": lower_body,
            "full_body": full_body,
            "profile_face": profile_face,
        }
