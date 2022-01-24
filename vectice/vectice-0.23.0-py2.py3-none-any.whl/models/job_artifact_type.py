from enum import EnumMeta


class JobArtifactType(EnumMeta):
    """
    Indicates whether the artifact is an input or an output of a run
    """

    INPUT = "INPUT"
    """
    """
    OUTPUT = "OUTPUT"
    """
    """
