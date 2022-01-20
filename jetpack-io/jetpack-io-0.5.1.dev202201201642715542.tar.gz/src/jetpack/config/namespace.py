from typing import Final, Optional

from jetpack.config import k8s

LOCAL_NAMESPACE: Final[str] = "local"


class NamespaceCache:
    def __init__(self) -> None:
        self.cache: Optional[str] = None

    def __call__(self) -> Optional[str]:
        if not k8s.is_in_cluster():
            return LOCAL_NAMESPACE
        if not self.cache:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
                self.cache = f.read().strip()
        return self.cache


get = NamespaceCache()
