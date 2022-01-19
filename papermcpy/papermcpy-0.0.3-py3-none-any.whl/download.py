from .utils import paper_request

__all__ = (
    'download'
)

def download(proj: str, ver: str, build: str, dl: str):
    return paper_request(type= "get", url = f"projects/{proj}/versions/{ver}/builds/{build}/downloads/{dl}")
