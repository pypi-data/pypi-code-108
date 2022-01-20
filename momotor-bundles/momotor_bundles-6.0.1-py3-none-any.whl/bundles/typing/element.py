import momotor.bundles

try:
    # Python 3.8+
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


class ElementMixinProtocol(Protocol):
    bundle: "momotor.bundles.Bundle"
