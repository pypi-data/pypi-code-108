# __version__ is placeholder
# It gets set in the build/publish process (publish_with_credentials.sh)
__version__ = "0.5.1-dev202201251643109094"

from jetpack._remote.interface import remote
from jetpack._task.interface import function, jet, jetroutine, schedule
from jetpack.cmd import root
from jetpack.redis import redis


def run() -> None:
    # options can be passed in as env variables with JETPACK prefix
    # e.g. JETPACK_ENTRYPOINT
    root.cli(auto_envvar_prefix="JETPACK")
