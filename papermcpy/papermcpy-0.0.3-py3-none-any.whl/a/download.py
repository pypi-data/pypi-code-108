from .utils import paper_request

__all_ = (
    'download'
)

async def download(proj: str, ver: str, build: str, dl: str):
    return await paper_request(type= "get", url = f"projects/{proj}/versions/{ver}/builds/{build}/downloads/{dl}")
