class _Data:
    """
    dict-key names that should not be passed
    - '_item_names'
    - '_to_dict'
    """
    def __init__(self, **kwargs):
        self._item_names = []
        for name, value in kwargs.items():
            if name.isalpha():
                exec(f"""self.{name} = value""")
                self._item_names.append(name)
            else:
                raise ValueError(f"dict-key cannot contain non-alphanumeric characters. key: {name}")
    
    def _to_dict(self):
        _out = {}
        for name in self._item_names:
            _out[name] = eval(f"self.{name}")
        return _out
