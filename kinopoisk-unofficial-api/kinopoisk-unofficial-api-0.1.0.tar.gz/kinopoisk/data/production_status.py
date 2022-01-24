from dataclasses import dataclass
import enum


class ProdactionStatus(enum.Enum):
    filming = 'FILMING'
    preprodaction = 'PRE_PRODUCTION'
    completed = 'COMPLETED'
    announced = 'ANNOUNCED'
    unknow = 'UNKNOWN'
    postprodaction = 'POST_PRODUCTION'
