import os

from redis_namespace import StrictRedis

host = os.environ.get("JETPACK_SHARED_REDIS_ADDRESS", "localhost")
slug = os.environ.get("JETPACK_SLUG", "global-bad")
pulumi_stack = os.environ.get("JETPACK_PULUMI_STACK", "dev")

namespace = ":".join([slug, pulumi_stack]) + ":"

redis = StrictRedis(host=host, namespace=namespace)
