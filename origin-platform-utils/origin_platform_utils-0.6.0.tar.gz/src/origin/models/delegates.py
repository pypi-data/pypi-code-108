from dataclasses import dataclass

from origin.serialize import Serializable


@dataclass
class MeteringPointDelegate(Serializable):
    """
    An actor (identified by its subject) who has been delegated
    access to a MeteringPoint (identified by its GSRN number).
    """
    subject: str
    gsrn: str

    # TODO Define time period (???)
