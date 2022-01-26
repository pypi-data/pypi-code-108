

import objgraph


previous_snapshot = {}


def take_snapshot():
    global previous_snapshot
    snapshot = {t: c for (t, c) in objgraph.most_common_types(limit=100)}
    print("Took snapshot of objgraph")
    if previous_snapshot:
        delta = {t: snapshot[t] - previous_snapshot.get(t, 0) for t in snapshot.keys()}
        print("Types with the most changes : ")
        for t in sorted(delta.keys(), key=lambda x: delta[x], reverse=True):
            if delta[t]:
                print("{0:20} {1}".format(t, delta[t]))
    previous_snapshot = snapshot


def show_chain(ob):
    objgraph.show_chain(objgraph.find_backref_chain(ob, objgraph.is_proper_module))
