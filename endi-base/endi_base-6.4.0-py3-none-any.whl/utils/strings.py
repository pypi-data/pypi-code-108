import locale


def format_quantity(quantity):
    """
        format the quantity
    """
    if quantity is not None:
        result = locale.format_string('%g', quantity, grouping=True)
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        return result
    else:
        return ""
