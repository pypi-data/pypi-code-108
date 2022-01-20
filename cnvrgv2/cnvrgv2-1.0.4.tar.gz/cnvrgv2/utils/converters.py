class StorageUnits:
    B = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"


def convert_bytes(bytes_to_convert, unit=None):
    """
    converts the given bytes to the given unit, or to the biggest non fraction unit.
    @param bytes_to_convert: bytes value to convert
    @param unit: unit to convert to, from STORAGE_UNITS Enum
    @return: The converted value and the unit
    """
    B = float(bytes_to_convert)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    units_table = {
        "B": B,
        "KB": KB,
        "MB": MB,
        "GB": GB,
        "TB": TB
    }

    if unit is not None:
        if unit == "B" or B == 0:
            return B, unit
        return B/units_table[unit], unit

    converted_result = None
    if B < KB:
        converted_result = B, StorageUnits.B
    elif KB <= B < MB:
        converted_result = B/KB, StorageUnits.KB
    elif MB <= B < GB:
        converted_result = B/MB, StorageUnits.MB
    elif GB <= B < TB:
        converted_result = B/GB, StorageUnits.GB
    elif TB <= B:
        converted_result = B/TB, StorageUnits.TB

    return converted_result
