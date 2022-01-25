import os
from operator import itemgetter
from pathlib import Path

from sm.misc.deser import deserialize_yml


class OntNS:
    """A helper class for converting absolute uri to relative uri
    """
    instance = None

    def __init__(self):
        default_infile = Path(__file__).absolute().parent.parent / "data/namespaces.yml"
        infile = os.environ.get('OntNSFile', default_infile)
        if infile is not None:
            assert os.path.exists(infile)
        self.prefix2uri = dict(deserialize_yml(infile))
        # uri and prefix sorted by the length of uri
        self.uri_and_prefix = sorted([(uri, prefix) for prefix, uri in self.prefix2uri.items()], key=itemgetter(0),
                                     reverse=True)

    @staticmethod
    def get_instance() -> 'OntNS':
        if OntNS.instance is None:
            OntNS.instance = OntNS()
        return OntNS.instance

    def get_abs_uri(self, rel_uri: str):
        prefix, name = rel_uri.split(":", 2)
        return self.prefix2uri[prefix] + name

    def get_rel_uri(self, abs_uri: str):
        # default strategy, can make it faster by parsing the url and filter by the domain
        for uri, prefix in self.uri_and_prefix:
            if abs_uri.startswith(uri):
                return f"{prefix}:{abs_uri.replace(uri, '')}"
        raise Exception(f"Cannot simply the uri `{abs_uri}` as its namespace is not defined")
