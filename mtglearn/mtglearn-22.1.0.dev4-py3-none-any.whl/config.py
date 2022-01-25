import os
from datasets.config import XDG_CACHE_HOME

DEFAULT_MTGLEARN_CACHE_HOME = os.path.join(XDG_CACHE_HOME, "mtglearn")
MTGLEARN_CACHE_HOME = os.path.expanduser(
    os.getenv("MTGLEARN_HOME", DEFAULT_MTGLEARN_CACHE_HOME)
)
