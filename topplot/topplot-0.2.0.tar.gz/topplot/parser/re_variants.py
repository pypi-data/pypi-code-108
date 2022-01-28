# ------------------------------------------------------------------------------
# Since top has variance in output across versions, handle regex variants


class Re_Variants:
    def __init__(self, name, first_entry, *, var_substs=None, scope=None):
        self._name = name
        self.index = 0
        self.re_arr = [first_entry]
        assert (
            var_substs is None or scope is not None
        ), "Re_Variants: var_substs given without corresponding scope"
        self.var_substs = [var_substs]
        self.scope = scope

    # --------------------------------------------------------------------------

    def append(self, re, var_substs=None, scope=None):
        self.re_arr.append(re)
        if var_substs is not None:
            assert (
                scope is not None or self.scope is not None
            ), "Re_Variants: var_substs given without corresponding scope"
            self.var_substs.append(var_substs)
            if scope:
                self.scope = scope

    # --------------------------------------------------------------------------

    def name(self):
        return self._name

    # --------------------------------------------------------------------------
    # Override match([..]) to fallback on regex variants
    def match(self, *args, **kwargs):
        i = self.index
        response = None

        while response is None and i < len(self.re_arr):
            response = self.re_arr[i].match(*args, **kwargs)
            if response is None:
                i += 1
            else:
                if i != self.index:
                    if self.var_substs[i] is not None:
                        for (var_name, var_value) in self.var_substs[i]:
                            # pylint: disable=exec-used
                            exec(f'{var_name}="{var_value}"', self.scope)

        if response is not None:
            self.index = i

        return response

    # --------------------------------------------------------------------------

    def pattern(self):
        return [regex.pattern for regex in self.re_arr]

    # --------------------------------------------------------------------------
    # Delegate all other functionality to current regex
    def __getattr__(self, attr):
        print(f"attr: >{attr}<")
        return getattr(self.re_arr[self.index], attr)


# ------------------------------------------------------------------------------
