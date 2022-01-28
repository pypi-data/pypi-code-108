class pdict(dict):
    def __getitem__(self, k, create=False):
        if not isinstance(k, list):
            return super().__getitem__(k)

        value = self
        for field in k:
            try:
                value = value.__getitem__(field)
            except KeyError as e:
                if create:
                    v = pdict({})
                    value.__setitem__(field, v)
                    value = value.__getitem__(field)
                else:
                    raise e

        return value

    def __setitem__(self, orgPath, v):
        if not isinstance(orgPath, list):
            return super().__setitem__(orgPath, v)
        value = self
        k = orgPath.copy()
        overwriteField = k.pop()
        for field in k:
            try:
                value = value.__getitem__(field)
            except KeyError:
                value.__setitem__(field, pdict())
                value = value.__getitem__(field)
        value[overwriteField] = v
