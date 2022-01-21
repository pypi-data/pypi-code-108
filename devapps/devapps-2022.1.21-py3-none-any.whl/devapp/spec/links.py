import json
import os

env = os.environ
_parsed = []
parsed_links = {}


def links():
    pl = parsed_links
    if not _parsed:
        with open(os.environ['build_dir'] + '/links.json') as fd:
            j = fd.read()
        parsed_links.update(json.loads(j))
        _parsed.append(True)
    return pl


# create string fid lists from classes list at build time:
full_id = lambda cls: [c.name for c in cls._parents]
fids = lambda clses: ['.'.join(full_id(co)) for co in clses]


def _get_via(for_, links, io, *caps, min=1, max=1000, **kw):
    """
    conn = lambda io, w: api.links.get_via(r, io, w, min=1)[0]
    httpapi = conn('in', 'api')
    """

    res = []
    for l in links[io]:
        have = [c for c in caps if c in l['via']['caps']]
        if len(have) == len(caps):
            v = dict(l['via'])
            # that can be list of strings (when loaded from links.json
            # or still a list of clses (at build time)
            # we return always the strings:
            c = l['cls']
            v['cls'] = [] if not c else c if isinstance(c[0], str) else fids(c)
            res.append(v)
    if len(res) < min or len(res) > max:
        msg = '%s: have %s links for %s %s, require min %s, max %s'
        msg = msg % (for_, len(res), '+'.join(caps), io, min, max)
        raise Exception(msg)
    return res


def get_via_by_r(r, io, *caps, min=1, max=1000):
    """Api method while rendering templates, (build time)"""
    return _get_via(r['___'], r['links'], io, *caps, min=min, max=max)


def get_via(io, *caps, min=1, max=1000, **kw):
    """Api method for apps, while running (run time)"""
    l = links()
    return _get_via(env['DA_CLS'], l, io, *caps, min=min, max=max, **kw)
