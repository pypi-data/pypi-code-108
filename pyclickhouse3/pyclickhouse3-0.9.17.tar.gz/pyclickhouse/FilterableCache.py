# -*- coding: utf-8 -*-
import sys
import logging
import datetime as dt

class FilterableCache(object):
    def __init__(self):
        self.data = {}
        self.index = {}

    def has_dataset(self, dataset_key):
        return dataset_key in self.data

    def add_dataset(self, dataset_key, primarykeys, rows):
        self.data[dataset_key] = dict([(tuple([row[field] for field in primarykeys]), row) for row in rows])
        key_info = []
        for i, _ in enumerate(primarykeys):
            key_info.append(set([x[i] for x in self.data[dataset_key].keys()]))
        self.index[dataset_key] = key_info

    def _recursivefoo(self, result, key, level, dataset_key):
        if level >= len(key):
            if level < len(self.index[dataset_key]):
                for existing_val in self.index[dataset_key][level]:
                    subkey = list(key)
                    subkey.append(existing_val)
                    subkey = tuple(subkey)
                    self._recursivefoo(result, subkey, level + 1, dataset_key)
            else:
                if key in self.data[dataset_key]:
                    result.append(self.data[dataset_key][key])
        else:
            if isinstance(key[level], slice):
                if isinstance(key[level].start, int) and isinstance(key[level].stop, int):
                    for x in range(key[level].start, key[level].stop):
                        subkey = list(key)
                        subkey[level] = x
                        subkey = tuple(subkey)
                        self._recursivefoo(result, subkey, level+1, dataset_key)
                elif isinstance(key[level].start, dt.date) and isinstance(key[level].stop, dt.date):
                    for x in range(0, (key[level].stop - key[level].start).days):
                        subkey = list(key)
                        subkey[level] = key[level].start + dt.timedelta(days=x)
                        subkey = tuple(subkey)
                        self._recursivefoo(result, subkey, level+1, dataset_key)
                else:
                    raise Exception('Only tuples of int or datetime.date are supported in filter')
            elif isinstance(key[level], list) or isinstance(key[level], tuple):
                for x in key[level]:
                    subkey = list(key)
                    subkey[level] = x
                    subkey = tuple(subkey)
                    self._recursivefoo(result, subkey, level + 1, dataset_key)
            else:
                self._recursivefoo(result, key, level + 1, dataset_key)

    def select(self, dataset_key, filter):
        keys = sorted(filter.keys())
        filtertuple = tuple([filter[field] for field in keys])
        result = []
        self._recursivefoo(result, filtertuple, 0, dataset_key)
        return result

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    data = FilterableCache()
    data.add_dataset('test', ['Color','Size'], [
        {'Color': 'red', 'Size': 10, 'Price': 300},
        {'Color': 'red', 'Size': 11, 'Price': 330},
        {'Color': 'red', 'Size': 12, 'Price': 360},
        {'Color': 'green', 'Size': 10, 'Price': 300},
        {'Color': 'green', 'Size': 11, 'Price': 330},
        {'Color': 'brown', 'Size': 10, 'Price': 100}])

    print(data.select('test', {'Color': 'red', 'Size': 10}))
    print()
    print(data.select('test', {'Color': 'red', 'Size': (10, 12, 555)}))
    print()
    print(data.select('test', {'Color': 'red', 'Size': slice(10, 12)}))
    print()
    print(data.select('test', {'Color': ['red', 'green', 'not there'], 'Size': 10}))
    print()
    print(data.select('test', {'Color': 'red'}))
    print()