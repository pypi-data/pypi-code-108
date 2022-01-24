from enum import EnumMeta


class JobType(EnumMeta):
    """
    Indicates the type of the job
    """

    EXTRACTION = "EXTRACTION"
    """
    """
    PREPARATION = "PREPARATION"
    """
    """
    TRAINING = "TRAINING"
    """
    """
    INFERENCE = "INFERENCE"
    """
    """
    DEPLOYMENT = "DEPLOYMENT"
    """
    """
    OTHER = "OTHER"
    """
    """
