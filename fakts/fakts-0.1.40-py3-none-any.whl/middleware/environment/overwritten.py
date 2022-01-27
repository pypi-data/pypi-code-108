import os

from fakts.middleware.base import FaktsMiddleware
import logging


logger = logging.getLogger(__name__)


def parse_env_value_to_python(value: str):
    if value in ("True", "true"):
        return True
    if value in ("false", "False"):
        return False
    return value


class OverwrittenEnvMiddleware(FaktsMiddleware):
    """Takes the previous Grants input
    and checks for environmental overwrites


    Args:
        FaktsGrant ([type]): [description]
    """

    def __init__(self, prepend=None, delimiter="_") -> None:
        super().__init__()
        self.prepend = prepend
        self.delimiter = delimiter

    async def aparse(self, previous={}, **kwargs):

        updated = {}
        try:
            for key, value in os.environ.items():
                if self.prepend:
                    if not key.startswith(self.prepend):
                        continue
                    key = key[len(self.prepend) :]

                path = list(map(lambda x: x.lower(), key.split(self.delimiter)))
                if path[0] in previous:
                    ref = updated
                    for part in path[:-1]:
                        if part not in ref:
                            ref[part] = {}
                        ref = ref[part]
                    ref[path[-1]] = value

        except Exception as e:
            logger.exception(e)

        return updated
