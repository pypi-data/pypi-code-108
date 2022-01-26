def format_size(size_in_bytes: int, precision: int = 0, binary_multiplier: bool = True) -> str:
    """
    Format a size (in bytes) into a human-readable format, with multipliers (KB, MB, GB, TB)
    Args:
        size_in_bytes (int): The size to format
        precision (int): Number of decimals
        binary_multiplier (bool): When true, use binary units (base 1024); when false, use decimal units (base 1000)

    Returns:
        string: formatted size
    """
    if size_in_bytes < 0:
        raise ValueError("Cannot format negative size")
    if precision < 0:
        raise ValueError("Precision must be non-negative")
    base_multiplier = 1 << 10 if binary_multiplier else 1000
    units = ["bytes", "KB", "MB", "GB", "TB"]
    for multiplier_exponent, unit in enumerate(units):
        precision_to_use = precision if multiplier_exponent > 0 else 0
        size_in_units = size_in_bytes / (base_multiplier ** multiplier_exponent)
        rounded_size_in_units = round(size_in_units, precision_to_use)
        if rounded_size_in_units < base_multiplier or multiplier_exponent + 1 >= len(units):
            return "{:.{}f} {}".format(rounded_size_in_units, precision_to_use, unit)
    raise RuntimeError("Unreachable code")
