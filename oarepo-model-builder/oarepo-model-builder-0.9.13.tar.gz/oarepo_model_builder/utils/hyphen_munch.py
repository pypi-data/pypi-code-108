from typing import Mapping

import munch


class HyphenMunch(munch.AutoMunch):
    def __setitem__(self, key, value):
        if isinstance(value, Mapping) and not isinstance(value, (munch.AutoMunch, munch.Munch)):
            value = munch.munchify(value, HyphenMunch)
        return super().__setitem__(key, value)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except:
            try:
                key = key.replace('_', '-')
                return super().__getitem__(key)
            except:
                key = key.replace('-', '_')
                return super().__getitem__(key)
