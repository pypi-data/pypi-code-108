import sys
import json
from argparse import Namespace

# https://mikefarah.gitbook.io/yq/usage/convert
# yq eval -o=j mindmap.yml | python mindmap.py

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def head(l):
    for x in l:
        return x

def merge_dicts(*ds):
    response = {}
    for d in ds:
        if isinstance(d, dict):
            response.update(d)
    return response

def merge_lists(*ls):
    response = []
    for l in ls:
        if isinstance(l, list):
            response = response + l
    return response

def recursive_print(obj, prefix="+", depth=2, style=''):
    # If its a string ...
    if isinstance(obj, str):
        print(f"{prefix*depth}{style} {obj}")
        return

    # If its a link obj
    if (
        isinstance(obj, dict) and 
        (len(obj.values()) == 1) and 
        (isinstance(head(obj.values()), str)) and 
        (head(obj.values()).startswith("http"))
    ):
        print(f"{prefix*depth}{style} [[{head(obj.values())} {head(obj.keys())}]]")
        return
    
    # If its a list ... 
    if isinstance(obj, list):
        for v in obj:
            recursive_print(v, prefix=prefix, depth=depth, style='_')
        return
        
    # Is a category or the root of a tool description
    if isinstance(obj, dict):
        # and all([isinstance(x, dict) for x in obj.values()])
        value_dict = merge_dicts(*merge_lists(*obj.values()))
        # eprint(*obj.values())
        # eprint(merge_lists(*obj.values()))
        # eprint(value_dict)
        for k, v in obj.items():
            node_class = "<<tool>>" if (("🖥" in value_dict) or ("📖" in value_dict)) else ""
            # Skip inner dicts ...
            if k in ["Uses Include", "Notes", "Questions"]:
                continue
            # if ("🖥" in value_dict) and ("📖" in value_dict):
            #     print(f"{prefix*depth}{style}: {k}\n[[{value_dict['🖥']} 🖥]]  |  [[{value_dict['📖']} 📖]] {node_class};")
            # el
            if "🖥" in value_dict:
                print(f"{prefix*depth}{style} [[{value_dict['🖥']} {k}]] {node_class}")
            else:
                print(f"{prefix*depth}{style} {k} {node_class}")
            recursive_print(v, prefix=prefix, depth=depth+1, style=style)
        return


# https://docs.python.org/3/library/json.html
# https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
# https://docs.python.org/dev/library/types.html#types.SimpleNamespace

# JSON = json.load(sys.stdin, object_hook=lambda o: Namespace(**o))
JSON = json.load(sys.stdin)

# print(json.dumps(JSON))

print('@startmindmap')
print("""
<style>
    mindmapDiagram {
        .tool {
            BackgroundColor lightblue
        }
    }
</style>
""")
print(f'+ **{JSON["Title"]}**')
# print(json.dumps(JSON["Right"], indent=4))
recursive_print(JSON["Right"])
print("'tag::left[]")
# print(json.dumps(JSON["Left"], indent=4))
recursive_print(JSON["Left"], "-")
print("'end::left[]")
print('@endmindmap')
