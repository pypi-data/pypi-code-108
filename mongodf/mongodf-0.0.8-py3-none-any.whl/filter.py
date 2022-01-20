from .exception import MongoDfException
import numpy as _np


class Filter():

    inversion_map = {
        "$in": "$nin",
        "$nin": "$in",
        "$gt": "$lte",
        "$lt": "$gte",
        "$gte": "$lt",
        "$lte": "$gt",
        "$eq": "$ne",
        "$ne": "$eq"
    }

    def __init__(self, dataframe, config, func=lambda x: x):
        self._mf = dataframe
        self.config = config
        self.func = func

    def __invert__(self):

        if len(self.config) != 1:
            raise MongoDfException(
                "Filter inversion only possible for single objects!")

        def sub_invert(ele):
            if "$elemMatch" in ele:
                return {"$elemMatch": sub_invert(ele["$elemMatch"])}
            else:
                if len(ele) != 1:
                    raise MongoDfException(
                        "Filter inversion only possible for single objects!")
                return {self.inversion_map[k]: v for k, v in ele.items()}

        new_filter = {k: sub_invert(v) for k, v in self.config.items()}

        return Filter(self._mf, new_filter, lambda x: _np.invert(self.func(x)))

    def __and__(self, filter_b):
        if self._mf._collection != filter_b._mf._collection:
            raise MongoDfException(
                "You cannot mix DataFrames during filtering")

        if len(self.config) > 0:
            if len(filter_b.config) == 0:
                return Filter(self._mf, self.config, self.func)

            if self._mf._array_expand:

                new_filter = filter_b.config.copy()
                for k, v in self.config.items():
                    if k in new_filter:
                        if "$elemMatch" in new_filter[k] and "$elemMatch" in v:
                            new_filter[k]["$elemMatch"].update(v["$elemMatch"])
                        else:
                            new_filter[k].update(v)
                    else:
                        new_filter[k] = v

            else:
                new_filter = filter_b.config.copy()
                for k, v in self.config.items():
                    if k in new_filter:
                        new_filter[k].update(v)
                    else:
                        new_filter[k] = v

            return Filter(self._mf, new_filter, lambda x: _np.logical_and(self.func(x), filter_b.func(x)))
        else:
            return Filter(self._mf, filter_b.config, filter_b.func)

    def __or__(self, filter_b):
        if self._mf._collection != filter_b._mf._collection:
            raise MongoDfException(
                "You cannot mix DataFrames during filtering")

        if len(self.config) > 0:
            if len(filter_b.config) == 0:
                return Filter(self._mf, self.config, self.func)

            new_filter = {"$or": [self.config.copy(), filter_b.config.copy()]}
            return Filter(self._mf, new_filter, lambda x: _np.logical_or(self.func(x), filter_b.func(x)))
        else:
            return Filter(self._mf, filter_b.config, filter_b.func)
