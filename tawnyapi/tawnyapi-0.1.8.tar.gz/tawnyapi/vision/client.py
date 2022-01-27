from tawnyapi.vision.face_detector import FaceDetector
from typing import List
import asyncio
import logging
import sys
import cv2
import aiohttp
import aiofiles
from . import apitypes
from .util import _get_base64_images, _load_images_from_paths, _resize_img, _get_resized_shape, _get_temp_folder, _get_square_from_box, _add_padding_to_box
from .face_detector import FaceDetector
import os
from tensorflow.keras.models import load_model
import numpy as np
import json


def _setup_logging(level=logging.DEBUG):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


logger = logging.getLogger(__name__)


class TawnyVisionApiClient:

    def __init__(self,
                 api_url: str = 'https://vision.tawnyapis.com',
                 api_key: str = None,
                 use_local_face_detection: bool = False,
                 use_local_face_embedding: bool = False,
                 sdk_version=apitypes.SdkVersion.V_1_4):
        self.async_client = TawnyVisionApiAsyncClient(
            api_url=api_url,
            api_key=api_key,
            use_local_face_detection=use_local_face_detection,
            use_local_face_embedding=use_local_face_embedding,
            sdk_version=sdk_version
        )

    def analyze_image_from_path(
            self,
            image_path: str,
            max_results: int = 1,
            resize: int = None,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):
        return asyncio.run(self.async_client.analyze_image_from_path(
            image_path=image_path,
            max_results=max_results,
            resize=resize,
            input_type=input_type,
            features=features
        ))

    def analyze_images_from_paths(
            self,
            image_paths: List[str] = [],
            max_results: int = 1,
            resize: int = None,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):
        return asyncio.run(self.async_client.analyze_images_from_paths(
            image_paths=image_paths,
            max_results=max_results,
            resize=resize,
            input_type=input_type,
            features=features
        ))

    def analyze_image(
            self,
            image,
            max_results: int = 1,
            resize: int = None,
            images_already_encoded=False,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):
        return asyncio.run(self.async_client.analyze_image(
            image=image,
            max_results=max_results,
            resize=resize,
            images_already_encoded=images_already_encoded,
            input_type=input_type,
            features=features
        ))

    def analyze_images(
        self,
            images=[],
            max_results: int = 1,
            resize: int = None,
            images_already_encoded=False,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):

        return asyncio.run(self.async_client.analyze_images(
            images=images,
            max_results=max_results,
            resize=resize,
            images_already_encoded=images_already_encoded,
            input_type=input_type,
            features=features
        ))


class TawnyVisionApiAsyncClient:

    def __init__(self,
                 api_url: str = 'https://vision.tawnyapis.com',
                 api_key: str = None,
                 use_local_face_detection: bool = False,
                 use_local_face_embedding: bool = False,
                 sdk_version: str = apitypes.SdkVersion.V_1_4):

        self._api_url = api_url
        self._api_key = api_key
        self._use_local_face_detection = use_local_face_detection
        self._use_local_face_embedding = use_local_face_embedding
        self._sdk_version = sdk_version

        self._face_detector = None
        self._emotion_embedding = None

        if self._use_local_face_embedding:
            asyncio.run(self.download_emotion_embedding())
            self._use_local_face_detection = True

        if self._use_local_face_detection:
            self._face_detector = FaceDetector()

    async def download_emotion_embedding(self):

        dirpath = _get_temp_folder()
        embedding_path = os.path.join(dirpath, 'embedding.model')

        try:
            if os.path.exists(embedding_path):
                self._emotion_embedding = load_model(
                    embedding_path, compile=False)
                return
        except:
            pass

        async with aiohttp.ClientSession() as session:
            url = self._api_url + '/v1/model/V_1_4/embedding/emotion'

            headers = {
                'Authorization': f'Bearer {self._api_key}'
            }

            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(embedding_path, mode='wb')
                        await f.write(await resp.read())
                        await f.close()
                        self._emotion_embedding = load_model(
                            embedding_path, compile=False)
            except:
                logging.error("Emedding Model cannot be downloaded!!!")

    async def analyze_image_from_path(
            self,
            image_path: str,
            max_results: int = 1,
            resize: int = None,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):
        return await self.analyze_images_from_paths(
            image_paths=[image_path],
            max_results=max_results,
            resize=resize,
            input_type=input_type,
            features=features
        )

    async def analyze_images_from_paths(
            self,
            image_paths: List[str] = [],
            max_results: int = 1,
            resize: int = None,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]

    ):

        images = _load_images_from_paths(image_paths, load_as_bytes=(
            not self._requires_local_processing(resize)))

        return await self.analyze_images(
            images=images,
            max_results=max_results,
            resize=resize,
            input_type=input_type,
            images_already_encoded=not self._requires_local_processing(resize),
            features=features
        )

    async def analyze_image(
            self,
            image,
            max_results: int = 1,
            resize: int = None,
            images_already_encoded=False,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):
        return await self.analyze_images(
            images=[image],
            max_results=max_results,
            resize=resize,
            images_already_encoded=images_already_encoded,
            input_type=input_type,
            features=features
        )

    async def analyze_images(
            self,
            images=[],
            max_results: int = 1,
            resize: int = None,
            images_already_encoded=False,
            input_type=apitypes.ImageInputType.RAW,
            features=[
                apitypes.ImageAnnotationFeatures.FACE_DETECTION,
                apitypes.ImageAnnotationFeatures.FACE_EMOTION
            ]
    ):

        # add feature FACE_DETECTION to features if features ATTENTION or HEAD_POSE are activated and FACE_DETECTION is missing and local face detection is false
        if (apitypes.ImageAnnotationFeatures.ATTENTION in features or apitypes.ImageAnnotationFeatures.HEAD_POSE in features) \
                and apitypes.ImageAnnotationFeatures.FACE_DETECTION not in features and not self._use_local_face_detection:
            features.append(apitypes.ImageAnnotationFeatures.FACE_DETECTION)

        images_base64 = []
        emotion_embeddings = []
        info_about_local_images = []
        rel_bounding_boxes = []

        if self._requires_local_processing(resize) and images_already_encoded:
            for idx, img in enumerate(images):
                nparr = np.fromstring(img, np.uint8)
                images[idx] = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            images_already_encoded = False

        if self._use_local_face_detection:
            faces = []
            for img in images:
                img = _resize_img(img, resize=resize)
                rects = self._face_detector.detect_faces(img)
                rects.sort(key=lambda r: (r[2]-r[0])*(r[3]-r[1]), reverse=True)

                faces_in_img = 0
                img_rects = []
                for (x1, y1, x2, y2) in rects[:max_results]:
                    sq_x1, sq_y1, sq_x2, sq_y2 = _get_square_from_box(
                        bounding_box=(x1, y1, x2, y2))

                    if self._use_local_face_embedding:
                        face = img[sq_y1:sq_y2, sq_x1:sq_x2]
                        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                        arr = _resize_img(face, resize=224, same_size=True)
                        arr = np.asarray(arr, dtype=np.float32) / 255.0
                        arr = np.expand_dims(arr, 0)

                        embedding = self._emotion_embedding(
                            arr, training=False)
                        data = embedding[0].numpy().tolist()

                        emotion_embeddings.append(json.dumps(data))
                    else:
                        _x1, _y1, _x2, _y2 = _add_padding_to_box(
                            bounding_box=(x1, y1, x2, y2), image_shape=img.shape, scale=1.60)

                        face_with_padding = img[_y1:_y2, _x1:_x2]
                        faces.append(face_with_padding)

                        rel_bounding_boxes.append({
                            'x1': int(sq_x1 - _x1),
                            'y1': int(sq_y1 - _y1),
                            'x2': int(sq_x2 - _x1),
                            'y2': int(sq_y2 - _y1)
                        })

                    img_rects.append((x1, y1, x2, y2))
                    faces_in_img += 1

                info_about_local_images.append(
                    {'faces_in_img': faces_in_img, 'rects': img_rects})

            # remove feature face_detection from features because of local use of face detection
            features = list(filter(
                lambda f: f != apitypes.ImageAnnotationFeatures.FACE_DETECTION, features))

            if self._use_local_face_embedding:
                # remove features beacause of local face_detection and face_embedding
                images_base64 = emotion_embeddings
                input_type = apitypes.ImageInputType.FACE_EMBEDDING
                features = list(filter(
                    lambda f: f != apitypes.ImageAnnotationFeatures.FACE_DESCRIPTOR, features))
                features = list(filter(
                    lambda f: f != apitypes.ImageAnnotationFeatures.FACE_LANDMARKS, features))
            else:
                images_base64 = _get_base64_images(images=faces, resize=None)

        else:
            images_base64 = _get_base64_images(
                images=images, resize=resize, images_already_encoded=images_already_encoded)

        request_data = {
            'requests': []
        }
        for idx, img in enumerate(images_base64):
            face_bounding_boxes = []
            if self._use_local_face_detection and not self._use_local_face_embedding:
                face_bounding_boxes = [rel_bounding_boxes[idx]]

            request_data['requests'].append({
                'image': img,
                'imageInputType': input_type,
                'features': features,
                'faceBoundingBoxes': face_bounding_boxes,
                'sdkVersion': self._sdk_version,
                'maxResults': max_results
            })

        headers = {
            'Authorization': f'Bearer {self._api_key}'
        }

        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                self._api_url + '/v1/images',
                headers=headers,
                json=request_data
            )

            result = await resp.json()

            if resp.status != 200:
                if 'detail' not in result:
                    result['detail'] = f"Error occurred - status code {resp.status}."
                return result

            if self._use_local_face_detection:
                restructured_result = {}

                restructured_result['images'] = []
                idx = 0
                # iterate over images
                for i, info_about_img in enumerate(info_about_local_images):
                    # iterate over faces in image
                    n = info_about_img['faces_in_img']
                    restructured_result['images'].append({'faces': []})
                    for j in range(0, n):
                        current_face = result['images'][idx]['faces'][0]

                        rect = {
                            'x1': info_about_img['rects'][j][0],
                            'y1': info_about_img['rects'][j][1],
                            'x2': info_about_img['rects'][j][2],
                            'y2': info_about_img['rects'][j][3]
                        }
                        current_face['boundingBox'] = rect
                        restructured_result['images'][i]['faces'].append(
                            current_face)
                        idx += 1

                    if 'debugInfo' in result['images'][i]:
                        restructured_result['images'][i]['debugInfo'] = None
                    if 'performanceInfo' in result['images'][i]:
                        restructured_result['images'][i]['performanceInfo'] = None

                if 'debugInfo' in result:
                    restructured_result['debugInfo'] = result['debugInfo']
                if 'performanceInfo' in result:
                    restructured_result['performanceInfo'] = result['performanceInfo']

                result = restructured_result

            result = self._adjust_face_rects_to_original_size(
                result_dict=result, resize=resize, orignal_images=images, features=features)
            return result

    def _adjust_face_rects_to_original_size(self, result_dict, resize=None, orignal_images=[], features=[]):

        for i, o_img in enumerate(orignal_images):

            r = 1
            if resize is not None:
                (_, _, r) = _get_resized_shape(
                    resize=resize, original_img_shape=o_img.shape)

            for j, _ in enumerate(result_dict['images'][i]['faces']):
                face = result_dict['images'][i]['faces'][j]
                x1 = int(face['boundingBox']['x1'] / r)
                x2 = int(face['boundingBox']['x2'] / r)
                y1 = int(face['boundingBox']['y1'] / r)
                y2 = int(face['boundingBox']['y2'] / r)

                (s_x1, s_y1, s_x2, s_y2) = _get_square_from_box(
                    bounding_box=(x1, y1, x2, y2))

                result_dict['images'][i]['faces'][j]['boundingBox']['x1'] = x1
                result_dict['images'][i]['faces'][j]['boundingBox']['x2'] = x2
                result_dict['images'][i]['faces'][j]['boundingBox']['y1'] = y1
                result_dict['images'][i]['faces'][j]['boundingBox']['y2'] = y2

                if apitypes.ImageAnnotationFeatures.FACE_LANDMARKS in features:
                    for k, l in enumerate(face['landmarks']):
                        result_dict['images'][i]['faces'][j]['landmarks'][k] = [
                            s_x1 + int(l[0]/r) - x1, s_y1 + int(l[1]/r) - y1]

        return result_dict

    def _requires_local_processing(self, resize):
        return resize is not None or self._use_local_face_detection or self._use_local_face_embedding
