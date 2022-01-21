import httpx
from ..models.post import Post


async def get(self, domain: str, count: int = 5) -> list[Post]:
    r: httpx.Request = await self._get(
        "wall.get",
        domain=domain,
        count=count
    )
    
    posts = r.json()["response"]["items"]
    return [Post.parse_obj(post) for post in posts]
