import httpx
from ..models.song import Song


async def search(self, query: str, count: int = 50, auto_complete: bool = True) -> list[Song]:
    r: httpx.Request = await self._get(
        "audio.search",
        q=query,
        count=count,
        auto_complete=int(auto_complete)
    )
    
    songs = r.json()["response"]["items"]
    return [Song.parse_obj(song) for song in songs]
