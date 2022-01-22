import os
from DecenTT.IPFS.locales.IPFSLocalesExceptions import *


def onLoadEnv(path: str = None):
    import dotenv
    dotenv.load_dotenv() if path is None else dotenv.load_dotenv(dotenv_path=path)


def getBootstrapNodes(path: str = None) -> list:
    import re
    onLoadEnv(path=path)

    pat = re.compile("BOOTSTRAP")
    bs_keys = list(filter(pat.match, list(os.environ)))

    nodes = list()
    try:
        for i, key in enumerate(bs_keys):
            nodes.append(os.environ[key])
    except Exception as e:
        raise BootstrapNodeError(error=e)

    return nodes


def getIPFSHost() -> str:
    try:
        onLoadEnv()
        return os.environ["DEFAULT_HOST"]
    except Exception as e:
        return "127.0.0.1:5001"
