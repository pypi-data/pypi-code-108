from .utils import paper_request
from .classes import Project

__all__ = (
    'proj',
    'projs'
)

def proj(proj: str):
    r = paper_request(type= "get", url = f"projects/{proj}")
    return Project(*[r[x] for x in list(r.keys())])

def projs():
    return paper_request(type= "get", url = "projects")
