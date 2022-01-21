import re

# for link rewrites:
href_slash_start_single = re.compile(" href *= *'/", re.IGNORECASE)
href_slash_start_dbl = re.compile(' href *= *"/', re.IGNORECASE)
src_slash_start_single = re.compile(" src *= *'/", re.IGNORECASE)
src_slash_start_dbl = re.compile(' src *= *"/', re.IGNORECASE)


def rewrite_links(url, src, rewrites={}):
    """ fix absolute and relative links """
    prot, empty, host, path = url.split('/', 3)
    host = prot + '//' + host
    path = '/' + path
    if not path.endswith('/'):
        path = path + '/'

    # absolut links: insert the host
    # (href = "/..." -> href = "<host>/..."
    src = re.sub(href_slash_start_single, " href = '%s/" % host, src)
    src = re.sub(src_slash_start_single, " src = '%s/" % host, src)
    src = re.sub(href_slash_start_dbl, ' href = "%s/' % host, src)
    src = re.sub(src_slash_start_dbl, ' src = "%s/' % host, src)

    # fix relative links:
    # (href = "../../ -> go up the uri)
    uriparts = path.split('/')

    src = src.replace("'./", "'" + host + path)
    src = src.replace('"./', '"' + host + path)
    # do the '../../....' links:
    for hir in range(len(uriparts) - 2, 0, -1):
        rel = '../' * hir
        urip = '/'.join(uriparts[: -(hir + 1)]) + '/'
        src = src.replace("'%s" % rel, "'" + host + urip)
        src = src.replace('"%s' % rel, '"' + host + urip)

    for k, v in list(rewrites.items()):
        src = src.replace(k, v)

    return src


RE_SCRIPT_START = re.compile(r'<script', re.IGNORECASE)
RE_SCRIPT_END = re.compile(r'</script', re.IGNORECASE)


def neutralize_script_tags(src):
    res = re.sub(RE_SCRIPT_START, '<!-- SCRIPT NEUTRALIZED BY DEVAPPS', src)
    res = re.sub(RE_SCRIPT_END, '-- END SCRIPT NEUTRALIZED BY DEVAPPS', res)
    return res


if __name__ == '__main__':
    src = '''
<a href = "/foo.html">
<a href="/nospace.html">
<a href = '/foo.html'>
<a href='/nospace.html'>
<a src = "/foo.html">
<a src ='/foo.html'>

<a src = './foo1.html'>
<a src = "./foo1.html">

<a src = '../foo2.html'>
<a src = "../foo2.html">

<a src = '../../foo3.html'>
<a src = "../../foo3.html">

<a src = '../../../foo4.html'>
<a src = "../../../foo4.html">

<scripT attrs>evil stuff</sCriPt>
    '''
    src = neutralize_script_tags(src)
    res = rewrite_links('http://my.host/l1/l2/l3', src)

    assert '''<a href = "http://my.host/foo.html">''' in res
    assert '''<a href = "http://my.host/nospace.html">''' in res
    assert '''<a href = 'http://my.host/foo.html'>''' in res
    assert '''<a href = 'http://my.host/nospace.html'>''' in res
    assert '''<a src = "http://my.host/foo.html">''' in res
    assert '''<a src = 'http://my.host/foo.html'>''' in res

    assert '''<a src = 'http://my.host/l1/l2/l3/foo1.html'>''' in res
    assert '''<a src = "http://my.host/l1/l2/l3/foo1.html">''' in res

    assert '''<a src = 'http://my.host/l1/l2/foo2.html'>''' in res
    assert '''<a src = "http://my.host/l1/l2/foo2.html">''' in res

    assert '''<a src = 'http://my.host/l1/foo3.html'>''' in res
    assert '''<a src = "http://my.host/l1/foo3.html">''' in res

    assert '''<a src = 'http://my.host/foo4.html'>''' in res
    assert '''<a src = "http://my.host/foo4.html">''' in res

    assert (
        '''<!-- SCRIPT NEUTRALIZED BY DEVAPPS attrs>evil stuff-- END SCRIPT NEUTRALIZED BY DEVAPPS>'''
        in res
    )

    print('%s\nrewritten to\n%s' % (src, res))
    print(res)
