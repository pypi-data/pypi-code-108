
class CpdPath(ABC):
    _subclasses = []

    def __init_subclass__(cls, **kwargs):
        if kwargs:
            raise RuntimeError("Kwargs used when subclassing CpdPath!")
        CpdPath._subclasses.append(cls)

    @abstractmethod
    def __str__(self) -> str: ...

    @classmethod
    def from_string(cls: Type[Self], s: str) -> Self:
        if cls is not CpdPath:
            raise RuntimeError("Default from_string must be overwritten!")

        for subclass in CpdPath._subclasses:
            try:
                return subclass.from_string(s)
            except TypeError:
                continue

    @classmethod
    def try_from_string(cls: Type[Self], s: str) -> Optional[Self]:
        try:
            return cls.from_string(s)
        except TypeError:
            return None