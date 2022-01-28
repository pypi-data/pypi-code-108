_ALL_FCOS = {}

# An internal superclass of declarative Tecton Objects
class Fco:
    @classmethod
    def _register(cls, fco):
        _ALL_FCOS[fco._id] = fco

    @property  # type: ignore
    def _id(self) -> str:
        """
        The id of this Tecton Object.
        """
        raise NotImplementedError()
