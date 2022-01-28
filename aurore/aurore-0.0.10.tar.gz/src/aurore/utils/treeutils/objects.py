from typing import Union, Mapping, Sequence


def iterate_leaves(
    item: Union[str,float,int,Mapping,Sequence]
    )->Union[str,float,int]:
    if isinstance(item,(str,float,int)):
        yield item
    elif isinstance(item,dict):
        for leaf in item.values():
            yield from iterate_leaves(leaf)
    elif isinstance(item,(tuple,list)):
        for leaf in item:
            yield from iterate_leaves(leaf)
