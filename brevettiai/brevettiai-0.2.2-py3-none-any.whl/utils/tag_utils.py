def find(tree, key, value):
    items = tree.get("children", []) if isinstance(tree, dict) else tree
    for item in items:
        if item[key] == value:
            yield item
        else:
            yield from find(item, key, value)


def find_path(tree, key, value, path=()):
    items = tree.get("children", []) if isinstance(tree, dict) else tree
    for item in items:
        if item[key] == value:
            yield (*path, item)
        else:
            yield from find_path(item, key, value, (*path, item))

#
# class TagUtils:
#     __tags = []
#     __datasets = []
#     __tag2datasets = {}
#
#     @classmethod
#     def add_info(self, tags, datasets):
#         self.__tags.extend(tags)
#         self.__datasets.extend(datasets)
#         self.recalculate_caches()
#
#     @classmethod
#     def recalculate_caches(self):
#         for ds in self.__datasets:
#             tags = ds.get("tags", [])
#             for tag in tags:
#                 self.__tag2datasets.setdefault(tag["id"], set()).add(ds["id"])
