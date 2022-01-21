class AssertionError(Exception):
    """Exception object raised when assertion is failed
    args[0] consists of following dict key:values
        args[0]['field'] is fieldname.
        args[0]['position'] is a tuple where fielddata is stripped.
        args[0]['data'] is stripped string data.
        args[0]['value'] is translated data.
    """
    pass


class FixedFieldParser(object):
    """parse fixed field"""
    def __init__(self, form):
        """Initialize parser

        form is a format with a list of field descriptor
            [(name, width, type, (assertion)), ...]
            name is dict key name. if name is None, this field is not interpreted.
                If name starts with unserscore '_', this field is parsed and asserted,
                but is not added to the parsed object.
            width is field width
            type is function used to translate string, such as int, float, etc.
                If name is None, type is not used, but recoomended to be None.
            assertion is an optional object. If assertion is not given or None,
                nothing occurs. If assertion is not callable object,
                type(strdata)==assertion, otherwise assertion(type(strdata)) is tested.
                When the test fails, AssertionError is raised.
        """
        self.form = form
        # generate field structure
        self.struct = []
        pos = 0
        for f in self.form:
            n, w, t = f[0:3]
            if n is not None:
                if len(f) > 3:
                    a = f[3]
                    if not callable(a):
                        def factory(a):
                            def eq_(x):
                                return x == a
                            return eq_
                        a = factory(a)
                else:
                    a = None
                self.struct.append((n, (pos, pos+w), t, a))
            pos += w

    def parse(self, s):
        """parse string and return a parsed dict

        s is string object

        returns parsed object
        """
        obj = {}
        for k, (i, j), t, a in self.struct:
            v = t(s[i:j])
            if a and not(a(v)):
                raise AssertionError({'field': k, 'value': v, 'data': s[i:j],
                                      'position': (i, j)})
            if k[0] != '_':
                obj[k] = v

        return obj
