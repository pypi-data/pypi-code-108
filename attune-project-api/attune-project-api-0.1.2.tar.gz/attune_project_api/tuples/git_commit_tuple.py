from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class GitCommitTuple(Tuple):
    __tupleType__ = "attune.auto.GitCommitTuple"

    timestamp: str = TupleField()
    hash: str = TupleField()
    authorName: str = TupleField()
    authorEmail: str = TupleField()
    message: str = TupleField()
