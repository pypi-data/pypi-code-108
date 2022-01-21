"""
查看模块时，解释器会在3个主要位置搜索模块
1、当前目录
2、解释器的site-packages位置(这些目录包含你可能已经安装的第三方Python模块(也包括你自己写的模块))
3、标准库位置

取决于很多因素，解释器搜索位置2和位置3的顺序可能有变化
"""

def search4vowels(phrase:str) -> set:
    """Return any vowels found in an supplied word."""
    vowels = set('aeiou')
    return vowels.intersection(set(phrase))


def search4letters(phrase:str, letters:str='aeiou') -> set:
    """Return a set of the 'letters' found in 'phrase'."""
    return set(letters).intersection(set(phrase))
