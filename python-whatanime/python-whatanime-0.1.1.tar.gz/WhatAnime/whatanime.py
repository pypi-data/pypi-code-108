"""
Client class for the wrapper
author: Joker Hacker
"""
from json import JSONDecodeError
from typing import IO, Any, Dict, Tuple, Optional, Union
import requests
from requests import Response
from .exception import APIError, ImageSizeTooLargeError, InvalidToken, QuotaExceedError
from .types import User, WAResponse
class Client:
    """
    This class, interacts with the API

    Note:
        The API server has a global request rate limit of 60/min per IP address.
        Regardless of which url endpoint you're calling. This is always counted by IP address, even if you request with an API Key.
    
        The rate limit info is included in the HTTP header. If you hit this HTTP rate limit, 
        request would fail with HTTP 429 (Too Many Requests).

    Args:
        token (:obj:`str`, optional): The API token to use to make requests.
        host (:obj:`str`, optional): Hostname of the API to use incase you have your own server setup
            Defaults to `api.trace.moe`
    
    Raises:
        ValueError: If image is empty or Token invalid.
        ImageSizeTooLargeError: when given image size is larger than 10MB.
        QuotaExceedError: When you reached your Quota limit for your IP/Token or too many requests.
        APIError: When Image is corrupted or Something went wrong on API's end.
    """
    def __init__(self, token: Optional[str] , host: str = "https://api.trace.moe") -> None:
        
        
        self._host = host
        self._token = token

        self.session = requests.Session()

    def _make_request(self, path: str, method: str = "get", **kwargs: Dict[Any, Any]) -> Tuple[Union[Dict, str], Response]:
        req = self.session.request(method, f'{self._host}/{path}', **kwargs)

        if req.status_code in [200, 201]:
            try:
                return req.json(), req
            except JSONDecodeError:
                return req.text, req
        elif req.status_code == 400:
            raise ValueError("Image is empty")
        elif req.status_code == 402:
            raise APIError("It seems you are sending multiple requests which is above your concurrency limit,")
        elif req.status_code == 403:
            raise InvalidToken("Token Invalid")
        elif req.status_code == 413:
            raise ImageSizeTooLargeError("Please reduce the image size to less than 10MB")
        elif req.status_code == 429:
            raise QuotaExceedError("It seems you have exceed your quota limit or too many requests")
        elif req.status_code == 500:
            raise APIError("500: This maybe because the image is corrupted")
        elif req.status_code == 503:
            raise APIError("503: Something went wrong on the API's end")



    def get_me(self) -> User:
        """
        Let you check the search quota and limit for your account (with API key) or IP address (without API key).

        Returns:
            :class:`WhatAnime.types.User`: The Dictionary of User Data
        """        
        data, req = self._make_request("me")

        return User(**data)

    def search_url(self, url: str, anilist: bool) -> WAResponse: 
        """
        Search using url.

        Args:
            url (:obj:`str`): url of the image/video to use for request.
            anilist (:obj:`bool`, optional): Pass :obj:`True` if you want to include anilist information

        Returns:
            :class:`WhatAnime.types.WAResponse`: Response object from the server which contains frameCount, error and :class:`WhatAnime.types.Result` object
        """           
        if anilist:
            data, req = self._make_request(f"search?anilistInfo&url={url}")
        elif not anilist:
            data, req = self._make_request(f"search?url={url}")

        return WAResponse(**data)

    def search_file(self, image) -> WAResponse:
        """
        Search using file.

        Args:
            image (:obj:`str`): Pass the location of image/video file, ex: search_file("image.jpeg")

        Returns:
            :class:`WhatAnime.types.WAResponse`: Response object from the server which contains frameCount, error and :class:`WhatAnime.types.Result` object
        """
        data, req = self._make_request("search", method="post", files={"image": open(image, "rb")})

        return WAResponse(**data)                                       