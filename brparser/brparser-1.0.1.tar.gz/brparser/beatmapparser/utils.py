def clamp(value, min_, max_):
    assert(max_ >= min_)
    if value > max_:
        return max_
    if value < min_:
        return min_
    return value
