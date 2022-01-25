from typing import Iterable, List, Optional

from pathlib import Path

import validators
from rdflib import RDF, ConjunctiveGraph, URIRef


def _to_url(uri: URIRef) -> Optional[str]:
    """Extract checkable URL from URIRef"""
    # only consider the URL part before a potential '#'
    str_uri = str(uri.defrag())
    if validators.url(str_uri):
        return str_uri
    return None


def get_urls(filenames: List[Path]) -> Iterable[str]:
    g = ConjunctiveGraph()
    for fn in filenames:
        g.parse(fn)
    urirefs = set()
    # deduplicate before transformation, trades off memory for runtime
    for terms in g.quads():
        urirefs.update({f for f in terms if isinstance(f, URIRef)})
    for ref in urirefs:
        url = _to_url(ref)
        if url:
            yield url
