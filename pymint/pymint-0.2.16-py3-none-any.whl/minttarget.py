from typing import Optional

from parchmint.target import Target


class MINTTarget(Target):
    """Target class that abstracts Parchmint Target class"""

    def __init__(self, componentstring: str, portstring: Optional[str] = None) -> None:
        super(MINTTarget, self).__init__(None)
        self.component = componentstring
        self.port = portstring

    def to_MINT(self) -> str:
        """MINT formatted string of the target  <component_name, port>

        Returns:
            str: MINT string
        """
        ret = "{} {}".format(self.component, "" if self.port is None else self.port)
        return ret
