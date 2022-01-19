from .utils import paper_request
from .classes import Version, Build, FBuild, Family, FBuilds

__all__ = (
    'version',
    'build',
    'family',
    'family_builds'
)

def version(proj: str, ver: str):
    r = paper_request(type= "get", url = f"projects/{proj}/versions/{ver}")
    return Version(*[r[x] for x in list(r.keys())])

def build(proj: str, ver: str, build: str):
    r = paper_request(type= "get", url = f"projects/{proj}/versions/{ver}/builds/{build}")
    return Build(*[r[x] for x in list(r.keys())])

def family(proj: str, family: str):
    r = paper_request(type= "get", url = f"projects/{proj}/version_group/{family}")
    return Family(*[r[x] for x in list(r.keys())])

def family_builds(proj: str, family: str):
    r = paper_request(type= "get", url = f"projects/{proj}/version_group/{family}/builds")
    builds = []
    for b in r["builds"]:
        builds.append(FBuild(*[b[x] for x in list(b.keys())]))
    r["builds"] = builds
    return FBuilds(*[r[x] for x in list(r.keys())])
