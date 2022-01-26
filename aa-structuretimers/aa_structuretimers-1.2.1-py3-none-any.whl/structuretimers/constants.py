from enum import IntEnum


class EveCategoryId(IntEnum):
    STRUCTURE = 65


class EveGroupId(IntEnum):
    CONTROL_TOWER = 365
    MOBILE_DEPOT = 1246
    REFINERY = 1406


class EveTypeId(IntEnum):
    CUSTOMS_OFFICE = 2233
    IHUB = 32458
    TCU = 32226
