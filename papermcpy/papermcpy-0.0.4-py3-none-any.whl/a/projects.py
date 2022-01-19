from .utils import paper_request
from ..classes import Project

__all_ = (
    'proj',
    'projs'
)

async def proj(proj: str):
    r = await paper_request(type= "get", url = f"projects/{proj}")
    return Project(*[r[x] for x in list(r.keys())])

async def projs():
    return await paper_request(type= "get", url = "projects")
