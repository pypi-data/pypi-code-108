import os, argparse
import numpy as np
from PIL import Image, ImageFile
from tqdm import tqdm
import cv2
from dlib import get_frontal_face_detector, shape_predictor
from imutils import face_utils


def calc_black_region_ratio(PIL_img):
    img_array = np.asarray(PIL_img)
    ratio = np.mean((img_array[:, :, 0] == 0) & (img_array[:, :, 1] == 0) & (img_array[:, :, 2] == 0))
    return ratio

def points2landmarks(points):
    # see the following page for definition of annotation points
    # https://ibug.doc.ic.ac.uk/resources/300-W/
    jaw = points[0:17]
    right_eyebrow = points[17:22]
    left_eyebrow = points[22:27]
    nose = points[27:36]
    right_eye = points[36:42]
    left_eye = points[42:48]
    mouth = points[48:60]
    lip = points[60:68]

    landmarks = {
        'jaw': jaw,
        'right_eyebrow': right_eyebrow,
        'left_eyebrow': left_eyebrow,
        'nose': nose,
        'right_eye': right_eye,
        'left_eye': left_eye,
        'mouth': mouth,
        'lip': lip
    }
    return landmarks

class FaceLandmarkDetector(object):
    def __init__(self, landmark_predictor_path=None):
        if landmark_predictor_path:
            self.landmark_predictor_path = landmark_predictor_path
        else:
            self.landmark_predictor_path = "shape_predictor_68_face_landmarks.dat"

        self.detector = get_frontal_face_detector()
        self.predictor = shape_predictor(self.landmark_predictor_path)

    def detect(self, img, return_type='landmarks'):
        """
        detect face landmarks of a given image

        Parameters
        ----------
        img: PIL.Image, RGB

        Returns
        -------
        landmarks : dict of np.array (None, 2)
            e.g. landmarks['jaw'][:, 0] are the x-coordinates of jaw
            landmarks, and landmars['jaw'][:, 1] are the y-coorinates.
        """
        landmarks = []
        points_list = []
        dets, _, _ = self.detector.run(img, 0)
        if len(dets)==0:
            return None
        for rect in dets:
            points = self.predictor(img, rect)
            points = face_utils.shape_to_np(points)
            points_list.append(points)
            landmarks.append(points2landmarks(points))

        if return_type == 'points':
            return points_list
        return landmarks

class FaceCropper():
    def __init__(self, landmark_predictor_path, resolution, mirror_padding, check_resolution, upper_limit_of_black_region_ratio):
        self.resolution = resolution
        self.check_resolution = check_resolution
        self.mirror_padding = mirror_padding
        self.upper_limit_of_black_region_ratio = upper_limit_of_black_region_ratio
        self.face_landmark_detector = FaceLandmarkDetector(landmark_predictor_path)
        self.n_all = 0
        self.n_small = 0
        self.n_detected = 0
        self.n_not_detected = 0
        self.m_all_face = 0
        self.m_low_resolution = 0
        self.m_high_black_region_ratio = 0
        self.m_ok_face = 0

    def _crop_face_by_landmarks(self, input_img, landmark_points):
        input_img_array = np.asarray(input_img)
        left_eye = landmark_points[36:42].mean(axis=0)
        right_eye = landmark_points[42:48].mean(axis=0)
        mouth_left = landmark_points[48]
        mouth_right = landmark_points[54]

        center_eyes = (left_eye + right_eye) / 2 + 0.5
        mouth_center = (mouth_left + mouth_right) / 2 + 0.5
        left_eye_to_right_eye = right_eye - left_eye
        eye_to_mouth = mouth_center - center_eyes

        new_x = left_eye_to_right_eye - np.array([-eye_to_mouth[1], eye_to_mouth[0]])
        new_x /= np.linalg.norm(new_x)
        new_x *= max(np.linalg.norm(left_eye_to_right_eye) * 2.0, np.linalg.norm(eye_to_mouth) * 1.8)
        length = np.linalg.norm(new_x)

        if self.check_resolution:
            if length * 2 <= self.resolution:
                return None

        # area expantion and translation to center
        move_xy = np.array((input_img.size[0] / 2, input_img.size[1] / 2))
        translated_img_size = (input_img.size[0] * 2, input_img.size[1] * 2)
        if self.mirror_padding == True:
          pad_w = input_img_array.shape[1]
          pad_h = input_img_array.shape[0]
          translated_img_array = np.pad(input_img_array, ((int(pad_h/2), int(pad_h/2)), (int(pad_w/2), int(pad_w/2)), (0, 0)), mode='reflect')
        else:
          translated_img_array = np.zeros((input_img.size[1] * 2, input_img.size[0] * 2, 3), dtype=np.uint8)
        index0 = (int(move_xy[1]), int(move_xy[1] + input_img.size[1]))
        index1 = (int(move_xy[0]), int(move_xy[0] + input_img.size[0]))
        translated_img_array[index0[0]:index0[1], index1[0]:index1[1] :] = input_img_array

        # rotate input_image on face_center
        face_center = center_eyes + eye_to_mouth * 0.1 + move_xy # translate face_center
        angle = 90 - np.degrees(np.arctan2(*new_x.tolist()))
        rotation_matrix = cv2.getRotationMatrix2D(tuple(face_center.tolist()), angle, scale=1)
        rotated_translated_img_array = cv2.warpAffine(translated_img_array, rotation_matrix, translated_img_size,
                                     flags=cv2.INTER_LANCZOS4)
        rotated_translated_img = Image.fromarray(rotated_translated_img_array)

        # crop and resize facial image
        cropped_points = [face_center[0] - length,
                          face_center[1] - length,
                          face_center[0] + length,
                          face_center[1] + length
                          ]
        cropped_img = rotated_translated_img.crop(cropped_points)
        return cropped_img

    def crop_face_from_path(self, image_path):
        '''
        crop image from given image_path.
        Input
            image_path: input image path  (dtype=str)
        Output
            cropped_image: cropped image (dtype=PIL.image)
        '''
        input_img = Image.open(image_path).convert("RGB")
        return self.crop_face_from_image(input_img)
    
    def crop_face_from_image(self, input_img):
        '''
        crop image from given input_img.
        Input
            input_img: input image (dtype=PIL.image)
        Output
            cropped_image: cropped image (dtype=PIL.image)
        '''
        self.n_all += 1

        input_img_array = np.asarray(input_img)
        flattened_landmarks_list = self.face_landmark_detector.detect(input_img_array, return_type='points')
        if flattened_landmarks_list is None:
#            print(image_path)
#            print("landmarks are not detected")
            self.n_not_detected += 1
            return None
        self.n_detected += 1

        cropped_imgs = []
        self.m_all_face += len(flattened_landmarks_list)
        for flattened_landmarks in flattened_landmarks_list:
            cropped_img = self._crop_face_by_landmarks(input_img, flattened_landmarks)
            if self.check_resolution:
                if cropped_img is None:
                    self.m_low_resolution += 1
 #                   print(image_path)
 #                   print('low resolution')

            if cropped_img is not None:
                black_region_ratio = calc_black_region_ratio(cropped_img)
                if black_region_ratio > self.upper_limit_of_black_region_ratio:
                    self.m_high_black_region_ratio += 1
                    cropped_img = None
                elif self.resolution == -1:
                    pass
                else:
                    self.m_ok_face += 1
                    cropped_img = cropped_img.resize((self.resolution, self.resolution),
                                                     resample=Image.LANCZOS)

            cropped_imgs.append(cropped_img)
        return cropped_imgs

    def summary(self):
        print('Resolution: %d' % self.resolution)
        print('Upper limit of black region ratio %.0f%%' % (self.upper_limit_of_black_region_ratio * 100))
        print()
        print('All images: %d' % self.n_all)
        print('Small images: %d(%.2f%%)' % (self.n_small, self.n_small / self.n_all * 100))
        print('Detected images: %d(%.2f%%)' % (self.n_detected, self.n_detected / self.n_all * 100))
        print('Not detected images: %d(%.2f%%)' % (self.n_not_detected, self.n_not_detected / self.n_all * 100))
        print()
        print('All faces: %d(%.2f%% for Detected images) ' % (self.m_all_face, self.m_all_face / self.n_detected * 100))
        print('OK faces: %d(%.2f%%)' % (self.m_ok_face, self.m_ok_face / self.m_all_face * 100))
        print('Low resolution faces: %d(%.2f%%)' % (self.m_low_resolution, self.m_low_resolution / self.m_all_face * 100))
        print('High black region ratio faces: %d(%.2f%%)' % (self.m_high_black_region_ratio, self.m_high_black_region_ratio / self.m_all_face * 100))
        print()
        print('OK faces / All images: %.2f%% ' % (self.m_ok_face / self.n_all * 100))


def calc_black_region_ratio(PIL_img):
    img_array = np.asarray(PIL_img)
    ratio = np.mean((img_array[:, :, 0] == 0) & (img_array[:, :, 1] == 0) & (img_array[:, :, 2] == 0))
    return ratio

def points2landmarks(points):
    # see the following page for definition of annotation points
    # https://ibug.doc.ic.ac.uk/resources/300-W/
    jaw = points[0:17]
    right_eyebrow = points[17:22]
    left_eyebrow = points[22:27]
    nose = points[27:36]
    right_eye = points[36:42]
    left_eye = points[42:48]
    mouth = points[48:60]
    lip = points[60:68]

    landmarks = {
        'jaw': jaw,
        'right_eyebrow': right_eyebrow,
        'left_eyebrow': left_eyebrow,
        'nose': nose,
        'right_eye': right_eye,
        'left_eye': left_eye,
        'mouth': mouth,
        'lip': lip
    }
    return landmarks

class FaceLandmarkDetector(object):
    def __init__(self, landmark_predictor_path=None):
        if landmark_predictor_path:
            self.landmark_predictor_path = landmark_predictor_path
        else:
            self.landmark_predictor_path = "shape_predictor_68_face_landmarks.dat"

        self.detector = get_frontal_face_detector()
        self.predictor = shape_predictor(self.landmark_predictor_path)

    def detect(self, img, return_type='landmarks'):
        """
        detect face landmarks of a given image

        Parameters
        ----------
        img: PIL.Image, RGB

        Returns
        -------
        landmarks : dict of np.array (None, 2)
            e.g. landmarks['jaw'][:, 0] are the x-coordinates of jaw
            landmarks, and landmars['jaw'][:, 1] are the y-coorinates.
        """
        landmarks = []
        points_list = []
        dets, _, _ = self.detector.run(img, 0)
        if len(dets)==0:
            return None
        for rect in dets:
            points = self.predictor(img, rect)
            points = face_utils.shape_to_np(points)
            points_list.append(points)
            landmarks.append(points2landmarks(points))

        if return_type == 'points':
            return points_list
        return landmarks

class FaceCropper:
    def __init__(self, landmark_predictor_path, resolution, mirror_padding, check_resolution, upper_limit_of_black_region_ratio):
        self.resolution = resolution
        self.check_resolution = check_resolution
        self.mirror_padding = mirror_padding
        self.upper_limit_of_black_region_ratio = upper_limit_of_black_region_ratio
        self.face_landmark_detector = FaceLandmarkDetector(landmark_predictor_path)
        self.n_all = 0
        self.n_small = 0
        self.n_detected = 0
        self.n_not_detected = 0
        self.m_all_face = 0
        self.m_low_resolution = 0
        self.m_high_black_region_ratio = 0
        self.m_ok_face = 0

    def _crop_face_by_landmarks(self, input_img, landmark_points):
        input_img_array = np.asarray(input_img)
        left_eye = landmark_points[36:42].mean(axis=0)
        right_eye = landmark_points[42:48].mean(axis=0)
        mouth_left = landmark_points[48]
        mouth_right = landmark_points[54]

        center_eyes = (left_eye + right_eye) / 2 + 0.5
        mouth_center = (mouth_left + mouth_right) / 2 + 0.5
        left_eye_to_right_eye = right_eye - left_eye
        eye_to_mouth = mouth_center - center_eyes

        new_x = left_eye_to_right_eye - np.array([-eye_to_mouth[1], eye_to_mouth[0]])
        new_x /= np.linalg.norm(new_x)
        new_x *= max(np.linalg.norm(left_eye_to_right_eye) * 2.0, np.linalg.norm(eye_to_mouth) * 1.8)
        length = np.linalg.norm(new_x)

        if self.check_resolution:
            if length * 2 <= self.resolution:
                return None

        # area expantion and translation to center
        move_xy = np.array((input_img.size[0] / 2, input_img.size[1] / 2))
        translated_img_size = (input_img.size[0] * 2, input_img.size[1] * 2)
        if self.mirror_padding == True:
          pad_w = input_img_array.shape[1]
          pad_h = input_img_array.shape[0]
          translated_img_array = np.pad(input_img_array, ((int(pad_h/2), int(pad_h/2)), (int(pad_w/2), int(pad_w/2)), (0, 0)), mode='reflect')
        else:
          translated_img_array = np.zeros((input_img.size[1] * 2, input_img.size[0] * 2, 3), dtype=np.uint8)
        index0 = (int(move_xy[1]), int(move_xy[1] + input_img.size[1]))
        index1 = (int(move_xy[0]), int(move_xy[0] + input_img.size[0]))
        translated_img_array[index0[0]:index0[1], index1[0]:index1[1] :] = input_img_array

        # rotate input_image on face_center
        face_center = center_eyes + eye_to_mouth * 0.1 + move_xy # translate face_center
        angle = 90 - np.degrees(np.arctan2(*new_x.tolist()))
        rotation_matrix = cv2.getRotationMatrix2D(tuple(face_center.tolist()), angle, scale=1)
        rotated_translated_img_array = cv2.warpAffine(translated_img_array, rotation_matrix, translated_img_size,
                                     flags=cv2.INTER_LANCZOS4)
        rotated_translated_img = Image.fromarray(rotated_translated_img_array)

        # crop and resize facial image
        cropped_points = [face_center[0] - length,
                          face_center[1] - length,
                          face_center[0] + length,
                          face_center[1] + length
                          ]
        cropped_img = rotated_translated_img.crop(cropped_points)
        return cropped_img

    def crop_face_from_path(self, image_path):
        '''
        crop image from given image_path.
        Input
            image_path: input image path  (dtype=str)
        Output
            cropped_image: cropped image (dtype=PIL.image)
        '''
        input_img = Image.open(image_path).convert("RGB")
        return self.crop_face_from_image(input_img)
    
    def crop_face_from_image(self, input_img):
        '''
        crop image from given input_img.
        Input
            input_img: input image (dtype=PIL.image)
        Output
            cropped_image: cropped image (dtype=PIL.image)
        '''
        self.n_all += 1

        input_img_array = np.asarray(input_img)
        flattened_landmarks_list = self.face_landmark_detector.detect(input_img_array, return_type='points')
        if flattened_landmarks_list is None:
#            print(image_path)
#            print("landmarks are not detected")
            self.n_not_detected += 1
            return None
        self.n_detected += 1

        cropped_imgs = []
        self.m_all_face += len(flattened_landmarks_list)
        for flattened_landmarks in flattened_landmarks_list:
            cropped_img = self._crop_face_by_landmarks(input_img, flattened_landmarks)
            if self.check_resolution:
                if cropped_img is None:
                    self.m_low_resolution += 1
 #                   print(image_path)
 #                   print('low resolution')

            if cropped_img is not None:
                black_region_ratio = calc_black_region_ratio(cropped_img)
                if black_region_ratio > self.upper_limit_of_black_region_ratio:
                    self.m_high_black_region_ratio += 1
                    cropped_img = None
                elif self.resolution == -1:
                    pass
                else:
                    self.m_ok_face += 1
                    cropped_img = cropped_img.resize((self.resolution, self.resolution),
                                                     resample=Image.LANCZOS)

            cropped_imgs.append(cropped_img)
        return cropped_imgs[0]


