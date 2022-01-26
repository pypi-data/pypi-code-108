import re

import voluptuous as vo


def DockerImage():
    def checker(value):
        m = re.compile(r"([a-z]+)/([a-z0-9-):([a-z0-9.]+)?").match(value)
        if m is None:
            raise vo.Invalid(f"Invalid Docker image: {value!r}")
        return value

    return checker


schema_resources = vo.Schema(
    {
        vo.Optional("workers", default=3): vo.All(int, vo.Range(min=1, max=100)),
        vo.Optional("memory", default=7): vo.All(int, vo.Range(min=1, max=1000)),
        vo.Optional("cpu", default=2): vo.All(int, vo.Range(min=1, max=1000)),
        vo.Optional("retries", default=0): vo.All(int, vo.Range(min=0, max=10)),
        vo.Optional("image"): DockerImage(),
    }
)

schema_pipeline = vo.Schema(
    {vo.Required("resources"): schema_resources}, extra=vo.ALLOW_EXTRA
)
