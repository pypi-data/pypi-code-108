__version__ = "0.1.1"
import requests
from .exceptions import PrismicRepoNameMissing


class Client(object):
    def __init__(self, repo_name):
        if repo_name is None:
            raise PrismicRepoNameMissing
        self.ref_url = f"https://{repo_name}.prismic.io/api/v2"
        self.url = f"https://{repo_name}.prismic.io/api/v2/documents/search"
        self.get_refs()

    def get_refs(self):
        """Get references for querying Prismic."""
        response = requests.get(self.ref_url)
        data = response.json()
        self.refs = data["refs"]

    def get_ref(self, ref="master"):
        """Return active ref."""
        for ref in self.refs:
            if ref["label"].lower() == "master":
                return ref
        return None

    def query(self, ref="master", predicate=None, **kwargs):
        """Run a query using Prismic predicate."""
        target_ref = self.get_ref(ref)
        payload = dict(
            ref=target_ref["ref"],
            pageSize=kwargs.get("pageSize"),
            page=kwargs.get("page"),
            after=kwargs.get("after"),
            fetch=kwargs.get("fetch"),
            fetchLinks=kwargs.get("fetchLinks"),
            lang=kwargs.get("lang"),
            orderings=kwargs.get("orderings"),
            q=predicate,
        )
        response = requests.get(self.url, params=payload)
        return response.json()
