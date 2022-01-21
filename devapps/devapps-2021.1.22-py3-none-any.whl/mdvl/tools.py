def to_md_list(shorts, keys, funcs, details):
    """helper for max explain and absl flags parser"""
    # if 'temporary' in str(funcs):
    #    breakpoint()  # FIXME BREAKPOINT
    if not shorts:
        return ''
    sep = ' `|` ' if any([s for s in shorts if s]) else ' '
    w = max([len(k) for k in keys])
    ws = max([len(k) for k in shorts])
    out = []
    for s, k, f, det in zip(shorts, keys, funcs, details):
        if f.startswith('[') and ']' in f:
            d, f = f.split(']', 1)
        f = d + ']`%s`' % f  # low color
        out.append('* %s%s%s`:` %s' % (s.ljust(ws), sep, k.ljust(w), f))
        if det:
            out[-1] += ' *Details: %s*' % det

    out.append('')
    return '\n'.join(out)


import os

import yaml


def add_metas(md_or_file, metas):
    if isinstance(metas, dict):
        metas = [(k, v) for k, v in metas.items()]

    if os.path.exists(md_or_file):
        with open(md_or_file) as fd:
            s = fd.read()
    else:
        s = md_or_file

    sep, m, body = get_meta(s)
    if not body:
        s = '\n'.join(('---', '', '---', '')) + s
    sep, m, body = get_meta(s)

    for k, v in metas:
        m[k] = v
    ls = '\n\n'
    return ''.join(
        (
            sep,
            ls,
            yaml.safe_dump(m, default_flow_style=False).strip(),
            ls,
            sep,
            ls,
            body.strip(),
        )
    )


def get_meta(s):
    try:
        sep = s.strip().split('\n')[0]
        s = '\n' + s
        l = s.split('\n%s\n' % sep, 3)
        assert not l[0].strip()
        if not l[1].strip():
            m = {}
        else:
            m = yaml.safe_load(l[1])
        return sep, m, l[2]
    except:
        return None, None, None


def struct_code_block(d, title=None):
    r = '\n```yaml\n%s\n```\n\n' % yaml.dump(d, default_flow_style=False)
    if not title:
        return r
    s = '''
<details>
 <summary>%s</summary>
%s
</details>
    '''
    return s % (title, r)


if __name__ == '__main__':
    for md in (
        '#foo\nbody',
        '''
---
foo: bar
bar: baz
---

body
    ''',
        'foo',
    ):
        m = {'dict': {'a': 'b'}}
        md = add_metas(md, m)
        import os

        m['Env'] = dict(os.environ)
        md = add_metas(md, m)
        print(add_metas(md, (('a', 'b'),)))


# .
