# Claudio Perez
import re, os
import fnmatch
import logging
from pathlib import Path
from itertools import product

from . import jsonpointer

from aurore.utils.treeutils import iterate_leaves

logger = logging.getLogger("aurore.selectors")


class Pattern:
    def __init__(self, pattern):
        self.pattern = pattern

    def validate(self,field)->bool:
        if isinstance(field,(str,float,int)):
            logger.debug(f"{self.pattern}, {field}")
            return fnmatch.fnmatch(field,self.pattern)
        else:
            return self.pattern == field


class PathBuilder:
    """
    Examples
    --------
    >>> item = {'id': 'xyz-123', 'a': {'b': 'c'}}
    >>> PathBuilder('%i/inter/file.rst').resolve(item)
    Path('xyz-123/inter/file.rst')
    >>> PathBuilder('%%:id/inter/%%:a:b/file.rst').resolve(item)
    Path('xyz-123/inter/c/file.rst')
    """
    def __init__(self,
        template: str,
        delimeter: str = "/",
        pointer_delimeter:str = ":",
        unpack_fields:bool = False
    ):
        self.template = template.split(delimeter)
        self.pointer_delimeter = pointer_delimeter
        # self.pointers = [
        #     Pointer(k) for k in self.template if "%" in k
        # ]

    def resolve(self,item)->str:
        return os.path.sep.join([
            Pointer(s,delimeter=self.pointer_delimeter).resolve(item)
                if "%" in s else s for s in self.template
        ])

    def resolve_recursively(self,item):
        components = [
            [*Pointer(s,delimeter=self.pointer_delimeter).resolve_recursively(item)]
              if "%" in s else [s] for s in self.template
        ]
        for combo in product(*components):
            yield os.path.sep.join(combo)


class Pointer:
    token_keys = {
        "c": lambda i,_: i["categories"],
        "t": lambda i,_: i["title"],
        "i": lambda i,_: i["id"],
        ".": lambda i,_: i,
        "%": lambda i,_: i,
    }
    attrib_tokens = {
        "s": lambda tree: tree.attrib["src"],
        "b": lambda tree: tree.attrib["base"]
    }

    def __init__(self, pointer:str,
        recurse=False,maxlen:int=30,truncate:bool=False,
        bracket_as_slice=False, delimeter="/"
    ):
        self.recurse:  bool = recurse
        self.truncate: bool = truncate
        self.slice:   slice = slice(maxlen)
        self.delimeter = delimeter
        if bracket_as_slice:
            match = re.search(r"\[(.*)\]$",pointer)
            if match:
                slice_str = match.group(1)
                self.slice = slice(*[
                    {True: lambda n: None, False: int}[x == ''](x)
                        for x in (slice_str.split(':') + ['', '', ''])[:3]
                ])
                pointer = pointer.rsplit("[",1)[0]
                logger.debug(f"slice_str: {slice_str}")
                logger.debug(f"slice: {self.slice}")

        if pointer[0] == "%":
            self.tokens = re.split(
                "([%|{0}][^{0}]*)".format("\\" + delimeter if delimeter in ["."] else delimeter
            ), pointer)[1::2]

            logger.debug(f"tokens: {self.tokens}")
        else:
            raise Exception(
                f"Unimplemented pattern handler for pointer: "
                f"{pointer}"
                )

    def resolve_tokens(self,item):
        for token in self.tokens:
            if re.match("^%.*", token):
                item = Pointer.token_keys[token[1]](item,None)
            else:
            # elif re.match("^/.*",token):
                item = jsonpointer.resolve_pointer(item, token, delim=self.delimeter)
        return item

    def resolve(self,item):
        base = self.resolve_tokens(item)
        return base[self.slice] \
            if self.truncate and isinstance(base,str) \
            else base

    def resolve_recursively(self,item):
        base = self.resolve_tokens(item)
        for i in iterate_leaves(base):
            yield i

class TrueSelector:
    def __init__(self, *args, **kwds):
        pass 
    def validate(self, item)->bool:
        return True

class FalseSelector:
    def __init__(self, *args, **kwds):
        pass 
    def validate(self, item)->bool:
        return False

class Selector:
    def __init__(self,selector:str):

        if ":" in selector:
            recurse = True
            pointer, pattern = selector.split(":")
        elif "=" in selector:
            recurse = False
            pointer, pattern = selector.split("=")
        else:
            recurse = False
            pointer, pattern = r"%i", selector

        self.pattern = Pattern(pattern)
        self.pointer = Pointer(pointer,recurse=recurse)
        self.recurse = recurse


    def validate(self,item):
        if self.recurse:
            return any(
                self.pattern.validate(val)
                    for val in self.pointer.resolve_recursively(item)
            )
        else:
            return self.pattern.validate(self.pointer.resolve(item))


def check_includes(args, item):
    logger.debug(args.include_item)
    if args.include_item:
        inclusive_selectors = [Selector(i) for i in args.include_item]
    else:
        inclusive_selectors = [TrueSelector()]
    
    if args.include_exclusive:
        exclusive_selectors = [Selector(i) for i in args.include_exclusive]
    else:
        exclusive_selectors = [TrueSelector()]
    
    if args.exclude_item:
        exclude_selectors = [Selector(i) for i in args.exclude_item]
    else:
        exclude_selectors = [FalseSelector()]

    
    return any(selector.validate(item) for selector in inclusive_selectors) \
           and \
           all(selector.validate(item) for selector in exclusive_selectors) \
           and \
           all(not selector.validate(item) for selector in exclude_selectors)

