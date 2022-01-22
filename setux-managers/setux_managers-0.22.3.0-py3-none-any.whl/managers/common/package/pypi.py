from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
from re import compile

from pybrary.html import Parser

from setux.targets import Local
from setux.logger import error, info


class Pypi:
    def __init__(self, pip):
        self.pip = pip

    def cache(self):
        local = Local(outdir=self.pip.cache_dir)
        url = 'https://pypi.org/simple'
        org = f'{self.pip.cache_dir}/pypi.simple'
        local.download(url=url, dst=org)
        pat = compile(r'^.*?<a href="/simple/.*?/">(?P<name>.*?)</a>')
        with open(self.pip.cache_file, 'w') as out:
            for line in open(org):
                try:
                    name = pat.search(line).groupdict()['name']
                    out.write(f'{name} -\n')
                except AttributeError: pass
        local.file(org).rm()

    def search(self, pattern):
        url = "https://pypi.org/search"
        query = urlencode({'q':pattern})

        req = Request(url+'?'+query)
        try:
            rsp = urlopen(req)
        except HTTPError as x:
            error('HTTP Error code: ', x.code)
        except URLError as x:
            error('URL ERROR Reason: ', x.reason)
        else:
            html = rsp.read().decode('utf-8')

        parser = Parser()
        root = parser.load(html)

        for pkg in (n for n in root if 'package-snippet' in n.classes):
            for node in (n for n in pkg if 'package-snippet__name' in n.classes):
                name = node.text
            for ver in (n for n in pkg if 'package-snippet__version' in n.classes):
                version = ver.text

            yield name, version
