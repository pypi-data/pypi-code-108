import httpx
from ..models.song import Song


async def get(self, owner_id: int, count: int = 1000) -> list[Song]:
    r: httpx.Request = await self._get(
        "audio.get",
        owner_id=owner_id,
        count=count
    )
    
    songs = r.json()["response"]["items"]
    return [Song.parse_obj(song) for song in songs]
