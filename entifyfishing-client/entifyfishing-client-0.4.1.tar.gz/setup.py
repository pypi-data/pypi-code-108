# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['entifyfishing_client',
 'entifyfishing_client.api',
 'entifyfishing_client.api.knowledge_base',
 'entifyfishing_client.api.query_processing',
 'entifyfishing_client.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.1.0,<22.0.0',
 'httpx>=0.15.4,<0.21.0',
 'python-dateutil>=2.8.0,<3.0.0']

setup_kwargs = {
    'name': 'entifyfishing-client',
    'version': '0.4.1',
    'description': 'A client library for accessing Entity-fishing - Entity Recognition and Disambiguation',
    'long_description': '# entifyfishing-client\nA client library for accessing [Entity-fishing](https://github.com/kermitt2/entity-fishing) - Entity Recognition and Disambiguation\n\n## Usage\nFirst, create a client:\n\n```python\nfrom entifyfishing_client import Client\n\nclient = Client(base_url="http://nerd.huma-num.fr/nerd/service")\n```\n\nNow call your endpoint and use your models:\n\n```python\nfrom entifyfishing_client.api.knowledge_base import get_concept, term_lookup\nfrom entifyfishing_client.api.query_processing import disambiguate\nfrom entifyfishing_client.models import (\n    Concept,\n    DisambiguateForm,\n    Language,\n    QueryParameters,\n    QueryResultFile,\n    QueryResultTermVector,\n    QueryResultText,\n    TermSenses,\n)\nfrom entifyfishing_client.types import File\n\nform = DisambiguateForm(\n    query=QueryParameters(\n        text="""Austria invaded and fought the Serbian army at the Battle of Cer and Battle of Kolubara beginning on 12 August. \n            The army, led by general Paul von Hindenburg defeated Russia in a series of battles collectively known as the First Battle of Tannenberg (17 August – 2 September). \n            But the failed Russian invasion, causing the fresh German troops to move to the east, allowed the tactical Allied victory at the First Battle of the Marne. \n            Unfortunately for the Allies, the pro-German King Constantine I dismissed the pro-Allied government of E. Venizelos before the Allied expeditionary force could arrive.\n            """,\n        language=Language(lang="en"),\n        mentions=["ner", "wikipedia"],\n        nbest=False,\n        customisation="generic",\n        min_selector_score=0.2,\n    )\n)\nr = disambiguate.sync_detailed(client=client, multipart_data=form)\nif r.is_success:\n    result: QueryResultText = r.parsed\n    assert result is not None\n    assert len(result.entities) > 0\n    assert result.entities[0].raw_name == "Austria"\n    assert result.entities[0].wikidata_id == "Q40"\n    \nr = get_concept.sync_detailed(id="Q40", client=client)\nresult: Concept = r.parsed\nif r.is_success:\n    assert result is not None\n    assert result.raw_name == "Austria"\n    assert result.wikidata_id == "Q40"    \n    assert len(result.statements) > 0\n```\n\nOr do the same thing with an async version:\n\n```python\npdf_file = "MyPDFFile.pdf"\nwith pdf_file.open("rb") as fin:\n    form = DisambiguateForm(\n        query=QueryParameters(\n            language=Language(lang="en"),\n            mentions=["wikipedia"],\n            nbest=False,\n            customisation="generic",\n            min_selector_score=0.2,\n            sentence=True,\n            structure="grobid",\n        ),\n        file=File(file_name=pdf_file.name, payload=fin, mime_type="application/pdf"),\n    )\n    r = await disambiguate.asyncio_detailed(client=client, multipart_data=form)\n    if r.is_success:\n        result: QueryResultFile = r.parsed\n        assert result is not None\n        assert len(result.entities) > 0\n        assert len(result.pages) > 0\n        assert len(result.entities[0].pos) > 0\n```\n\nBy default, when you\'re calling an HTTPS API it will attempt to verify that SSL is working correctly. Using certificate verification is highly recommended most of the time, but sometimes you may need to authenticate to a server (especially an internal server) using a custom certificate bundle.\n\n```python\nclient = Client(\n    base_url="http://nerd.huma-num.fr/nerd/service", \n    verify_ssl="/path/to/certificate_bundle.pem",\n)\n```\n\nYou can also disable certificate validation altogether, but beware that **this is a security risk**.\n\n```python\nclient = Client(\n    verify_ssl=False\n)\n```\n\nThings to know:\n1. Every path/method combo becomes a Python module with four functions:\n    1. `sync`: Blocking request that returns parsed data (if successful) or `None`\n    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.\n    1. `asyncio`: Like `sync` but the async instead of blocking\n    1. `asyncio_detailed`: Like `sync_detailed` by async instead of blocking\n\n1. All path/query params, and bodies become method arguments.\n1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)\n1. Any endpoint which did not have a tag will be in `entifyfishing_client.api.default`\n\n## Building / publishing this Client\nThis project uses [Poetry](https://python-poetry.org/) to manage dependencies  and packaging.  Here are the basics:\n1. Update the metadata in pyproject.toml (e.g. authors, version)\n1. If you\'re using a private repository, configure it with Poetry\n    1. `poetry config repositories.<your-repository-name> <url-to-your-repository>`\n    1. `poetry config http-basic.<your-repository-name> <username> <password>`\n1. Publish the client with `poetry publish --build -r <your-repository-name>` or, if for public PyPI, just `poetry publish --build`\n\nIf you want to install this client into another project without publishing it (e.g. for development) then:\n1. If that project **is using Poetry**, you can simply do `poetry add <path-to-this-client>` from that project\n1. If that project is not using Poetry:\n    1. Build a wheel with `poetry build -f wheel`\n    1. Install that wheel from the other project `pip install <path-to-wheel>`\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
