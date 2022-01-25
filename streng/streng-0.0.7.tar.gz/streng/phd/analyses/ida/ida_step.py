from dataclasses import dataclass


@dataclass
class IdaStep:
    base_record: str
    pga: float
    loss_index: float
    collapse: bool

    # ενδεχομένως να βάλω ως μεταβλητή την class με τα αποτελέσματα της ανάλυσης
