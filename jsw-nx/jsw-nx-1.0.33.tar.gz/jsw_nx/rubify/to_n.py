def to_n(string):
    try:
        return int(string)
    except ValueError:
        return float(string)
