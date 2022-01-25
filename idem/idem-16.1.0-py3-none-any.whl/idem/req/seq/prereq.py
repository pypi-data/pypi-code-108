def run(hub, seq, low, running):
    """
    Process the prereq system
    """
    pres = {}
    for ind, data in seq.items():
        if "prereq" not in data["chunk"]:
            continue
        chunk = data["chunk"]
        tag = data["tag"]
        pres[tag] = set()
        for rdef in chunk["prereq"]:
            state = next(iter(rdef))
            name = rdef[state]
            r_chunks = hub.idem.tools.get_chunks(low, state, name)
            for r_chunk in r_chunks:
                r_tag = hub.idem.tools.gen_tag(r_chunk)
                pres[tag].add(r_tag)
                reqret = {
                    "name": name,
                    "state": state,
                    "r_tag": r_tag,
                    "req": "prereq",
                    "chunk": r_chunk,
                    "ret": {},
                }
                data["reqrets"].append(reqret)
    if not pres:
        return seq
    unmet = {}
    for ind, data in seq.items():
        for tag, r_tags in pres.items():
            if tag not in unmet:
                unmet[tag] = set()
            if data["tag"] in r_tags:
                # Found one!
                if data["unmet"]:
                    unmet[tag].update(data["unmet"])
                else:
                    data["unmet"].add(tag)
    for ind, data in seq.items():
        tag = data["tag"]
        if tag in unmet:
            data["unmet"].update(unmet[tag])
    return seq
