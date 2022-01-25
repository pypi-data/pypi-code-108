import json
from abc import abstractmethod
from collections import Callable
from io import BytesIO
from typing import Optional, Union, BinaryIO, List
from urllib.parse import urljoin

import magic
import requests
from pydantic import BaseModel, validate_arguments
from requests import Response
from requests.auth import HTTPBasicAuth
from requests_toolbelt.multipart import encoder


class DefaultS3Image(BaseModel):
    bucket: str
    object_name: str
    order: int


class ImageList(BaseModel):
    title: str
    description: str
    data: dict


class VideoList(BaseModel):
    title: str
    description: str
    data: dict


class Novel(BaseModel):
    title: str
    data: dict

    def dict(self, *args, **kwargs):
        d = super(Novel, self).dict(*args, **kwargs)
        d["data"] = json.dumps(d["data"])
        return d


class BaseClient:
    def __init__(self, endpoint: str, user: str, password: str):
        self._password = password
        self._user = user
        self._endpoint = endpoint

    @property
    def _auth(self):
        return HTTPBasicAuth(self._user, self._password)

    def make_url(self, url):
        return urljoin(self._endpoint, url)

    def method_wrapper(self, func: Callable, url: str, *args, **kwargs):
        kwargs["auth"] = self._auth
        return func(self.make_url(url), *args, **kwargs)

    def get(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.get, url, *args, **kwargs)

    def post(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.post, url, *args, **kwargs)

    def put(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.put, url, *args, **kwargs)

    def delete(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.delete, url, *args, **kwargs)

    def patch(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.patch, url, *args, **kwargs)


class BaseMediaClient(BaseClient):

    @abstractmethod
    def get_route_name(self) -> str: pass

    def __init__(self, endpoint: str, user: str, password: str, object_id: int):
        super().__init__(endpoint, user, password)
        self.object_id = object_id

    @property
    def reaction(self) -> Optional[bool]:
        resp = self.get(
            f"api/{self.get_route_name()}/{self.object_id}/reaction"
        )
        resp.raise_for_status()
        return resp.json()["positive_reaction"]

    @reaction.setter
    def reaction(self, positive_reaction: Optional[bool]):
        resp = self.post(
            f"api/{self.get_route_name()}/{self.object_id}/reaction",
            json=dict(
                positive_reaction=positive_reaction
            )
        )
        resp.raise_for_status()

    @property
    def data(self):
        resp = self.get(f"api/{self.get_route_name()}/{self.object_id}")
        resp.raise_for_status()
        return resp.json()

    def destroy(self):
        self.delete(f"api/{self.get_route_name()}/{self.object_id}").raise_for_status()


class ImageListClient(BaseMediaClient):

    def get_route_name(self) -> str:
        return "imagelist"

    def __init__(self, endpoint: str, user: str, password: str, object_id: int):
        super().__init__(endpoint, user, password, object_id)

    def append_s3_images(self, images: List[DefaultS3Image]):
        self.post(
            f"api/image/upload",
            json=dict(
                image_list_id=self.object_id,
                default_s3_files=[
                    m.dict()
                    for m in images
                ]
            )
        ).raise_for_status()

    def upload_images(self, files: List[Union[bytes, str, BinaryIO]], order: int = 0):
        files_commit = {}
        for i, file in enumerate(files):
            if isinstance(file, str):
                with open(file, "rb") as fp:
                    data = fp.read()
            elif isinstance(file, bytes):
                data = file
            else:
                data = file.read()
            mime = magic.from_buffer(data, mime=True)
            files_commit[f"{i + order}"] = (str(i + order), BytesIO(data), mime)
        self.post(
            "api/image/upload",
            data=dict(image_list_id=self.object_id),
            files=files_commit
        ).raise_for_status()


class VideoListClient(BaseMediaClient):

    def get_route_name(self) -> str:
        return "videolist"

    def __init__(self, endpoint: str, user: str, password: str, object_id: int):
        super().__init__(endpoint, user, password, object_id)

    def upload_mp4_video(self, filename: str, order: int = 0):
        with open(filename, "rb") as fp:
            form = encoder.MultipartEncoder({
                "file": ("data.mp4", fp, "video/mp4"),
                "video_list_id": str(self.object_id),
                "order": str(order)
            })
            headers = {"Prefer": "respond-async", "Content-Type": form.content_type}
            self.post(
                "api/video/upload",
                headers=headers,
                data=form
            ).raise_for_status()

    def append_s3_video(self, bucket: str, object_name: str):
        self.post(
            "api/video/upload",
            json={
                "video_list_id": str(self.object_id),
                "bucket": bucket,
                "object_name": object_name,
            }
        ).raise_for_status()


class NovelClient(BaseMediaClient):

    def get_route_name(self) -> str:
        return "novel"

    def __init__(self, endpoint: str, user: str, password: str, object_id: int):
        super().__init__(endpoint, user, password, object_id)


class ResmanClient(BaseClient):
    def __init__(self, endpoint: str, user: str, password: str):
        super().__init__(endpoint, user, password)

    def get_image_list(self, object_id: int):
        return ImageListClient(
            self._endpoint,
            self._user,
            self._password,
            object_id=object_id
        )

    def get_video_list(self, object_id: int):
        return VideoListClient(
            self._endpoint,
            self._user,
            self._password,
            object_id=object_id
        )

    def get_novel(self, object_id: int):
        return NovelClient(
            self._endpoint,
            self._user,
            self._password,
            object_id=object_id
        )

    @validate_arguments
    def create_image_list(self, info: ImageList):
        resp = self.post(
            "api/imagelist",
            json=info.dict()
        )
        resp.raise_for_status()
        return self.get_image_list(int(resp.json()["id"]))

    @validate_arguments
    def create_video_list(self, info: VideoList):
        resp = self.post(
            "api/videolist",
            json=info.dict()
        )
        resp.raise_for_status()
        return self.get_video_list(int(resp.json()["id"]))

    @validate_arguments
    def create_novel(self, info: Novel, text: str):
        resp = self.post(
            "api/novel",
            data=info.dict(),
            files={"file": ("data.txt", BytesIO(text.encode()), "text/plain")}
        )
        resp.raise_for_status()
        return self.get_novel(int(resp.json()["id"]))
