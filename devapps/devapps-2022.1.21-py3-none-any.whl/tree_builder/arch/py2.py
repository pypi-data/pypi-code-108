def cls_with_meta(mc, attrs):
    class _x_(object):
        __metaclass__ = mc

    for k, v in attrs.items():
        setattr(_x_, k, v)
    return _x_
