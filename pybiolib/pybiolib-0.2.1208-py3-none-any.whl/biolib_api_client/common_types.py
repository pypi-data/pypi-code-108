from biolib.typing_utils import TypedDict


class SemanticVersion(TypedDict):
    major: int
    minor: int
    patch: int
