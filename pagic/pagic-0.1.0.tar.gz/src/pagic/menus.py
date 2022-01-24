from flask import request

from pagic.routing import url_for


def make_menu(menu_spec):
    path = request.path
    menu = []
    for d in menu_spec:
        endpoint = d["endpoint"]
        if endpoint.startswith("/"):
            url = endpoint
        else:
            url = url_for(endpoint)

        entry = {
            "label": d["label"],
            "url": url,
            "active": path.startswith(url),
            "tooltip": d.get("tooltip", ""),
        }
        menu.append(entry)

    return menu
