from lib2to3.pgen2.token import OP
from typing import Any, Dict, List, Optional, Union


class WhatAnimeType:
    """Base class for all WhatAnime objects
    """
    def __str__(self) -> str:
        return f'<{self.__class__.__name__}: {self.__dict__}>'

    def __repr__(self) -> str:
        return self.__str__()

class User(WhatAnimeType):
    """
    This object represents a User
    
    Args:
        id (:obj:`str`): User ID 
        priority (:obj:`int`): With limited processing power available, the server has priority queue to handle requests 
        concurrency (:obj:`int`): The number of simultaneous (parallel) requests you can make to the API server
        quota (:obj:`int`): Quota remaining for the IP or given token
        quotaUsed (:obj:`int`): Quota used for the IP or given token
    """
    id: str
    priority: int
    concurrency: int
    quota: int
    quotaUsed: int

    def __init__(
        self,
        id: str,
        priority: int,
        concurrency: int,
        quota: int,
        quotaUsed: int,
        **kwargs
    ) -> None:

        self.id = id
        self.priority = priority
        self.concurrency = concurrency
        self.quota = quota
        self.quotaUsed = quotaUsed

class Anilist(WhatAnimeType):
    id: int
    idMal: int
    title: Dict[str, str]
    synonyms: List[str]
    isAdult: bool

    def __init__(self, 
        id: int, 
        idMal: int, 
        title: Dict[str, str], 
        synonyms: List[str], 
        isAdult: bool,
        **kwargs
    ) -> None:
        self.id = id
        self.idMal = idMal
        self.title = title
        self.synonyms = synonyms
        self.isAdult = isAdult

class Result(WhatAnimeType):
    """
    This object represents a Result for :class:`WhatAnime.types.WAResponse`

    Args:
        anilist (:obj:`int` | :class:`WhatAnime.types.Anilist`): The matching anilist ID or Anilist Info, which contains information about
            id, idMal, title, synonyms and isAdult
            
        filename (:obj:`str`): The filename of file where the match is found
        episode (:obj:`Any`): The extracted episode number from filename.
        from_time (:obj:`int`): Starting time of the matching scene (seconds)
        to_time (:obj:`int`): Ending time of the matching scene (seconds)
        similarity (:obj:`int`): Similarity compared to search image
        video (:obj:`str`): URL to the preview video of the matching scene
        image (:obj:`str`): URL to the preview image of the matching scene
    """
    anilist: Union[int,Anilist]
    filename: str
    episode: Any
    from_time: int
    to_time: int
    similarity: int
    video: str
    image: str

    def __init__(
        self, 
        anilist: Union[int, Anilist], 
        filename: str,
        episode: Any,
        from_time: int,
        to_time: int,
        similarity: int,
        video: str,
        image: str,
        **kwargs
    ) -> None:
        self.anilist = anilist
        self.filename: filename
        self.episode = episode
        self.from_time = from_time
        self.to_time = to_time
        self.similarity = similarity
        self.video = video
        self.image = image


class WAResponse(WhatAnimeType):
    """
    This object represents Response from API.

    Args:
        frameCount (:obj:`int`); Total number of frames searched.
        error (:obj:`str`): Error Message
        result (:obj:`list`): List of :class:`WhatAnime.types.Result` Object, which containes all the information about the search request.
    """
    frameCount: int
    error: Optional[str]
    result: list[Result]

    def __init__(self, frameCount: int, error: Optional[str], result: list[Result], **kwargs):
        self.frameCount = frameCount
        self.error = error
        self.result = result