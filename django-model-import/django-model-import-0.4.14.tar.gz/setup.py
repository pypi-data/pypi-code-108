# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djangomodelimport']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.0.0,<4.0.0',
 'python-dateutil>=2.7.0,<3.0.0',
 'tablib>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'django-model-import',
    'version': '0.4.14',
    'description': "A Django library for importing CSVs and other structured data quickly using Django's ModelForm for validation and deserialisation into an instance.",
    'long_description': '# django-model-import\n\n[![PyPI version](https://badge.fury.io/py/django-model-import.svg)](https://badge.fury.io/py/django-model-import)\n[![Build Status](https://travis-ci.org/uptick/django-model-import.svg?branch=master)](https://travis-ci.org/uptick/django-model-import)\n\nDjango Model Import is a light weight CSV importer built for speed.\n\nIt uses a standard Django `ModelForm` to parse each row, giving you a familiar API to work with\nfor data validation and model instantiation. In most cases, if you already have a `ModelForm`\nfor the `ContentType` you are importing you do not need to create an import specific form.\n\nTo present feedback to the end-user running the import you can easily generate a preview\nof the imported data by toggling the `commit` parameter.\n\nIt also provides some import optimized fields for ForeignKey\'s, allowing preloading all\npossible values, or caching each lookup as it occurs, or looking up a model where multiple\nfields are needed to uniquely identify a resource.\n\n\n## Installation\n\n```bash\npoetry add django-model-import\n```\n\n\n## Quickstart\n\n```python\nimport djangomodelimport\n\nclass BookImporter(djangomodelimport.ImporterModelForm):\n    name = forms.CharField()\n    author = CachedChoiceField(queryset=Author.objects.all(), to_field=\'name\')\n\n    class Meta:\n        model = Book\n        fields = (\n            \'name\',\n            \'author\',\n        )\n\nwith default_storage.open(\'books.csv\', \'rb\') as fh:\n    data = fh.read().decode("utf-8")\n\n# Use tablib\nparser = djangomodelimport.TablibCSVImportParser(BookImporter)\nheaders, rows = parser.parse(data)\n\n# Process\nimporter = djangomodelimport.ModelImporter(BookImporter)\npreview = importer.process(headers, rows, commit=False)\nerrors = preview.get_errors()\n\nif errors:\n    print(errors)\n\nimportresult = importer.process(headers, rows, commit=True)\nfor result in importresult.get_results():\n    print(result.instance)\n```\n\n\n## Composite key lookups\n\nOften a relationship cannot be referenced via a single unique string. For this we can use\na `CachedChoiceField` with a `CompositeLookupWidget`. The widget looks for the values\nunder the `type` and `variant` columns in the source CSV, and does a unique lookup\nwith the field names specified in `to_field`, e.g. `queryset.get(type__name=type, name=variant)`.\n\nThe results of each `get` are cached internally for the remainder of the import minimising\nany database access.\n\n```python\nclass AssetImporter(ImporterModelForm):\n    site = djangomodelimport.CachedChoiceField(queryset=Site.objects.active(), to_field=\'ref\')\n    type = djangomodelimport.CachedChoiceField(queryset=AssetType.objects.filter(is_active=True), to_field=\'name\')\n    type_variant = djangomodelimport.CachedChoiceField(\n        queryset=InspectionItemTypeVariant.objects.filter(is_active=True),\n        required=False,\n        widget=djangomodelimport.CompositeLookupWidget(source=(\'type\', \'variant\')),\n        to_field=(\'type__name\', \'name\'),\n    )\n    contractor = djangomodelimport.CachedChoiceField(queryset=Contractor.objects.active(), to_field=\'name\')\n```\n\n\n## Flat related fields\n\nOften you\'ll have a OneToOneField or just a ForeignKey to another model, but you want to be able to\ncreate/update that other model via this one. You can flatten all of the related model\'s fields onto\nthis importer using `FlatRelatedField`.\n\n```python\nclass ClientImporter(ImporterModelForm):\n    primary_contact = FlatRelatedField(\n        queryset=ContactDetails.objects.all(),\n        fields={\n            \'contact_name\': {\'to_field\': \'name\', \'required\': True},\n            \'email\': {\'to_field\': \'email\'},\n            \'email_cc\': {\'to_field\': \'email_cc\'},\n            \'mobile\': {\'to_field\': \'mobile\'},\n            \'phone_bh\': {\'to_field\': \'phone_bh\'},\n            \'phone_ah\': {\'to_field\': \'phone_ah\'},\n            \'fax\': {\'to_field\': \'fax\'},\n        },\n    )\n\n    class Meta:\n        model = Client\n        fields = (\n            \'name\',\n            \'ref\',\n            \'is_active\',\n            \'account\',\n\n            \'primary_contact\',\n        )\n```\n\n## Tests\nRun tests with `python example/manage.py test testapp`\n',
    'author': 'Aidan Lister',
    'author_email': 'aidan@uptickhq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uptick/django-model-import',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
