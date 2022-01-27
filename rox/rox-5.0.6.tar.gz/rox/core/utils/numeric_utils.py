# Checks if a string value is numeric
def is_numeric(string_value):
    try:
        float(string_value)
        return True
    except Exception:
        return False

# Converts string value to float
def convert_to_float(string_value):
    return float(string_value)
