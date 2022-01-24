from . import DHW, DHW_CIRCUITS, ZONES, ZN

MAGIC_EASYCONTROL = bytearray.fromhex(
    "1d86b2631b02f2c7978b41e8a3ae609b0b2afbfd30ff386da60c586a827408e4"
)
EASYCONTROL = "EASYCONTROL"
PRODUCT_ID = "productID"
DEVICES = "devices"
DV = "dv"
CIRCUIT_TYPES = {DHW: DHW_CIRCUITS, ZN: ZONES, DV: DEVICES}
TARGET_TEMP = "targettemp"
PROGRAM_LIST = "programList"
IDLE = "idle"
TRUE = "true"
FALSE = "false"
USED = "used"
BOOLEAN = "boolean"
ENERGY = "energy"
PAGINATION = "pagination"
