from ..replayparser import Mod
def clamp(value, min_, max_):
    assert(max_ >= min_)
    if value > max_:
        return max_
    if value < min_:
        return min_
    return value

def apply_mods_to_diff(diff, hr_factor, mods):
    if Mod.EZ in mods:
        diff = max(0, diff / type(diff)(2))
    if Mod.HR in mods:
        diff = min(10, diff * type(diff)(hr_factor))
    return diff

def apply_mods_to_time(t, mods):
    if Mod.DT in mods:
        return t / type(t)(1.5)
    elif Mod.HT in mods:
        return t / type(t)(0.75)
    return t

def diff_range(diff, min_, mid, max_, mods):
    diff = apply_mods_to_diff(diff, 1.4, mods)

    if (diff > 5):
        return mid + (max_ - mid) * (diff - 5) / 5
    if (diff < 5):
        return mid - (mid - min_) * (5 - diff) / 5
    return mid
