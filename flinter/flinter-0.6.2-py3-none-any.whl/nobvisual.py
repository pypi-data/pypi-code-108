
from ctypes import c_int64
import tkinter as tk

from nobvisual import tkcirclify
from nobvisual.utils import path_as_str
from nobvisual.helpers import from_nested_struct_to_nobvisual


def visualfort(count_dict, minrate=-10, norate=False, start_mainloop=True):
    """Visualization of code structure in a circular packing.
    """

    nstruct = [tree2circ(count_dict, minrate=minrate, norate=norate)]

    circles = from_nested_struct_to_nobvisual(nstruct)

    if norate:
        colorscale = None
    else:
        colorscale = ("Standard compliance", "High (10)", f"Low ({str(minrate)})")

    draw_canvas = tkcirclify(
        circles,
        color="#eeeeee",
        colorscale=colorscale,
        title=f"Flinter showing {count_dict['path']}",
    )

    draw_canvas.show_names(level=2)

    if start_mainloop:
        tk.mainloop()


def tree2circ(tree, minrate=-20, norate=False, item_id=c_int64(-1)):
    """Translate the tree structure to a circlify object.
    """
    path_ls = tree["path"].split("/")
    text = path_as_str(path_ls)

    item_id.value += 1
    out = {
        "id": item_id.value,
        "datum": max(1, tree["size"]),
        "children": list(),
        "name": path_ls[-1],
        "text": text,
        "short_text": text,
    }

    for childtree in tree["children"]:
        out["children"].append(tree2circ(childtree, minrate=minrate,
                                         norate=norate, item_id=item_id))

    if not norate:
        out["text"] += f"\n\nsize: {tree['size']}"

        try:  # TODO: why the try?
            value = max((10 - tree["rate"]) / (10. - minrate), 0)
            rate_txt = f"\nrate: {tree['rate']:.2f}"
            out["text"] += rate_txt
            out["short_text"] += rate_txt
            out["color"] = f"colormap: {value}"
        except KeyError:
            out["color"] = "#ff0000"

    out["text"] += f"\n\n# regexp errors: {tree['regexp_nberr']}"
    out["text"] += f"\n# struct errors: {tree['struct_nberr']}"

    # detailed regexp count
    regex_txt = _get_detailed_rule_counts(tree['regexp_rules'],
                                          'regexp rules (#):')
    if regex_txt:
        out["text"] += f"\n{regex_txt}"

    # detailed struct count
    struct_txt = _get_detailed_rule_counts(tree['struct_rules'],
                                           'struct rules (#):')
    if struct_txt:
        out["text"] += f"\n{struct_txt}"

    return out


def _get_detailed_rule_counts(rules, title, sep='  '):
    info_var = ''
    for key, count in rules.items():
        info_var += f'\n{sep}{key}: {count}'

    if info_var:
        return f'\n{title}{info_var}'

    return info_var
