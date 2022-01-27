# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brickschema',
 'brickschema.bin',
 'brickschema.brickify',
 'brickschema.brickify.src',
 'brickschema.brickify.src.handlers',
 'brickschema.brickify.src.handlers.Handler',
 'brickschema.brickify.src.handlers.Handler.HaystackHandler',
 'brickschema.brickify.src.handlers.Handler.HaystackHandler.utils',
 'brickschema.brickify.src.handlers.Handler.RACHandler']

package_data = \
{'': ['*'],
 'brickschema': ['ontologies/1.1/*',
                 'ontologies/1.2/*',
                 'ontologies/1.2/alignments/*',
                 'ontologies/1.2/extensions/*',
                 'web/*'],
 'brickschema.brickify.src.handlers.Handler.HaystackHandler': ['conversions/*'],
 'brickschema.brickify.src.handlers.Handler.RACHandler': ['conversions/*']}

install_requires = \
['Flask>=1.1.2,<2.0.0',
 'Jinja2>=2.11.2,<3.0.0',
 'PyYAML>=5.3.1,<6.0.0',
 'click-spinner>=0.1.10,<0.2.0',
 'colorama>=0.4.4,<0.5.0',
 'dedupe>=2.0.8,<3.0.0',
 'importlib-resources>=3.3.0,<4.0.0',
 'owlrl>=6.0,<7.0',
 'pyshacl>=0.18,<0.19',
 'pytest>=6.2,<7.0',
 'rdflib>=6.1,<7.0',
 'requests>=2.25.0,<3.0.0',
 'sqlalchemy>=1.3,<2.0',
 'tabulate>=0.8.7,<0.9.0',
 'typer[all]>=0.3.2,<0.4.0',
 'xlrd>=1.2.0,<2.0.0']

entry_points = \
{'console_scripts': ['brick_validate = brickschema.bin.brick_validate:main',
                     'brickify = brickschema.brickify.main:app']}

setup_kwargs = {
    'name': 'brickschema',
    'version': '0.5.2a10',
    'description': 'A library for working with the Brick ontology for buildings (brickschema.org)',
    'long_description': '# Brick Ontology Python package\n\n![Build](https://github.com/BrickSchema/py-brickschema/workflows/Build/badge.svg)\n[![Documentation Status](https://readthedocs.org/projects/brickschema/badge/?version=latest)](https://brickschema.readthedocs.io/en/latest/?badge=latest)\n\nDocumentation available at [readthedocs](https://brickschema.readthedocs.io/en/latest/)\n\n## Installation\n\nThe `brickschema` package requires Python >= 3.6. It can be installed with `pip`:\n\n```\npip install brickschema\n```\n\nThe `brickschema` package offers several installation configuration options for reasoning.\nThe default bundled [OWLRL](https://pypi.org/project/owlrl/) reasoner delivers correct results, but exhibits poor performance on large or complex ontologies (we have observed minutes to hours) due to its bruteforce implementation.\n\nThe [Allegro reasoner](https://franz.com/agraph/support/documentation/current/materializer.html) has better performance and implements enough of the OWLRL profile to be useful. We execute Allegrograph in a Docker container, which requires the `docker` package. To install support for the Allegrograph reasoner, use\n\n```\npip install brickschema[allegro]\n```\n\nThe [reasonable Reasoner](https://github.com/gtfierro/reasonable) offers even better performance than the Allegro reasoner, but is currently only packaged for Linux and MacOS platforms. To install support for the reasonable Reasoner, use\n\n```\npip install brickschema[reasonable]\n```\n\n## Quickstart\n\nThe main `Graph` object is just a subclass of the excellent [RDFlib Graph](https://rdflib.readthedocs.io/en/stable/) library, so all features on `rdflib.Graph` will also work here.\n\nBrief overview of the main features of the `brickschema` package:\n\n```python\nimport brickschema\n\n# creates a new rdflib.Graph with a recent version of the Brick ontology\n# preloaded.\ng = brickschema.Graph(load_brick=True)\n# OR use the absolute latest Brick:\n# g = brickschema.Graph(load_brick_nightly=True)\n# OR create from an existing model\n# g = brickschema.Graph(load_brick=True).from_haystack(...)\n\n# load in data files from your file system\ng.load_file("mbuilding.ttl")\n# ...or by URL (using rdflib)\ng.parse("https://brickschema.org/ttl/soda_brick.ttl", format="ttl")\n\n# perform reasoning on the graph (edits in-place)\ng.expand(profile="owlrl")\ng.expand(profile="shacl") # infers Brick classes from Brick tags\n\n# validate your Brick graph against built-in shapes (or add your own)\nvalid, _, resultsText = g.validate()\nif not valid:\n    print("Graph is not valid!")\n    print(resultsText)\n\n# perform SPARQL queries on the graph\nres = g.query("""SELECT ?afs ?afsp ?vav WHERE  {\n    ?afs    a       brick:Air_Flow_Sensor .\n    ?afsp   a       brick:Air_Flow_Setpoint .\n    ?afs    brick:isPointOf ?vav .\n    ?afsp   brick:isPointOf ?vav .\n    ?vav    a   brick:VAV\n}""")\nfor row in res:\n    print(row)\n\n# start a blocking web server with an interface for performing\n# reasoning + querying functions\ng.serve("localhost:8080")\n# now visit in http://localhost:8080\n```\n\n## Features\n\n## Inference\n\n`brickschema` makes it easier to employ reasoning on your graphs. Simply call the `expand` method on the Graph object with one of the following profiles:\n- `"rdfs"`: RDFS reasoning\n- `"owlrl"`: OWL-RL reasoning (using 1 of 3 implementations below)\n- `"vbis"`: add VBIS tags to Brick entities\n- `"tag"`: infer Brick classes from Brick tags\n\n\n```python\nfrom brickschema import Graph\n\ng = Graph(load_brick=True)\ng.load_file("test.ttl")\ng.expand(profile="owlrl")\nprint(f"Inferred graph has {len(g)} triples")\n```\n\n\nThe package will automatically use the fastest available reasoning implementation for your system:\n\n- `reasonable` (fastest, Linux-only for now): `pip install brickschema[reasonable]`\n- `Allegro` (next-fastest, requires Docker): `pip install brickschema[allegro]`\n- OWLRL (default, native Python implementation): `pip install brickschema`\n\nTo use a specific reasoner, specify `"reasonable"`, `"allegrograph"` or `"owlrl"` as the value for the `backend` argument to `graph.expand`.\n\n## Haystack Translation\n\n`brickschema` can produce a Brick model from a JSON export of a Haystack model.\nThen you can use this package as follows:\n\n```python\nimport json\nfrom brickschema import Graph\nmodel = json.load(open("haystack-export.json"))\ng = Graph(load_brick=True).from_haystack("http://project-haystack.org/carytown#", model)\npoints = g.query("""SELECT ?point ?type WHERE {\n    ?point rdf:type/rdfs:subClassOf* brick:Point .\n    ?point rdf:type ?type\n}""")\nprint(points)\n```\n\n## VBIS Translation\n\n`brickschema` can add [VBIS](https://vbis.com.au/) tags to a Brick model easily\n\n```python\nfrom brickschema import Graph\ng = Graph(load_brick=True)\ng.load_file("mybuilding.ttl")\ng.expand(profile="vbis")\n\nvbis_tags = g.query("""SELECT ?equip ?vbistag WHERE {\n    ?equip  <https://brickschema.org/schema/1.1/Brick/alignments/vbis#hasVBISTag> ?vbistag\n}""")\n```\n\n## Web-based Interaction\n\n`brickschema` now supports interacting with a Graph object in a web browser. Executing `g.serve(<http address>)` on a graph object from your Python script or interpreter will start a webserver listening (by default) at http://localhost:8080 . This uses [Yasgui](https://yasgui.triply.cc/) to provide a simple web interface supporting SPARQL queries and inference.\n\n\n## Brick model validation\n\nThe module utilizes the [pySHACL](https://github.com/RDFLib/pySHACL) package to validate a building ontology against the Brick Schema, its default constraints (shapes) and user provided shapes.\n\n```python\nfrom brickschema import Graph\n\ng = Graph(load_brick=True)\ng.load_file(\'myBuilding.ttl\')\nvalid, _, _ = g.validate()\nprint(f"Graph is valid? {valid}")\n\n# validating using externally-defined shapes\nexternal = Graph()\nexternal.load_file("other_shapes.ttl")\nvalid, _, _ = g.validate(shape_graphs=[external])\nprint(f"Graph is valid? {valid}")\n```\n\nThe module provides a command\n`brick_validate` similar to the `pyshacl` command.  The following command is functionally\nequivalent to the code above.\n```bash\nbrick_validate myBuilding.ttl -s other_shapes.ttl\n```\n\n## `Brickify`\n\n**Usage**:\n\n```console\n$ brickify [OPTIONS] SOURCE\n```\n\n**Arguments**:\n\n* `SOURCE`: Path/URL to the source file  [required]\n\n**Options**:\n\n* `--input-type TEXT`: Supported input types: rac, table, rdf, haystack-v4\n* `--brick PATH`: Brick.ttl\n* `--config PATH`: Custom configuration file\n* `--output PATH`: Path to the output file\n* `--serialization-format TEXT`: Supported serialization formats: turtle, xml, n3, nt, pretty-xml, trix, trig and nquads  [default: turtle]\n* `--minify / --no-minify`: Remove inferable triples  [default: False]\n* `--input-format TEXT`: Supported input formats: xls, csv, tsv, url, turtle, xml, n3, nt, pretty-xml, trix, trig and nquads  [default: turtle]\n* `--building-prefix TEXT`: Prefix for the building namespace  [default: bldg]\n* `--building-namespace TEXT`: The building namespace  [default: https://example.com/bldg#]\n* `--site-prefix TEXT`: Prefix for the site namespace  [default: site]\n* `--site-namespace TEXT`: The site namespace  [default: https://example.com/site#]\n* `--install-completion`: Install completion for the current shell.\n* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n* `--help`: Show this message and exit.\n\nUsage examples: [brickify](tests/data/brickify).\n\n## Development\n\nBrick requires Python >= 3.6. We use [pre-commit hooks](https://pre-commit.com/) to automatically run code formatters and style checkers when you commit.\n\nUse [Poetry](https://python-poetry.org/docs/) to manage packaging and dependencies. After installing poetry, install dependencies with:\n\n```bash\npoetry install\n```\n\nEnter the development environment with the following command (this is analogous to activating a virtual environment.\n\n```bash\npoetry shell\n```\n\nOn first setup, make sure to install the pre-commit hooks for running the formatting and linting tools:\n\n```bash\n# from within the environment; e.g. after running \'poetry shell\'\npre-commit install\n```\n\nRun tests to make sure build is not broken\n\n```bash\n# from within the environment; e.g. after running \'poetry shell\'\nmake test\n```\n\n### Docs\n\nDocs are written in reStructured Text. Make sure that you add your package requirements to `docs/requirements.txt`\n',
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://brickschema.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
