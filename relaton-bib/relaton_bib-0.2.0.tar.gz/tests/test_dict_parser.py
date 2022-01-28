import os
import json
import yaml

from relaton_bib import from_dict


def test_create_bibitem_from_dict():
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "dict.json")

    with open(file) as json_file:
        reference = json.load(json_file)

        item = from_dict(reference)

        assert item is not None
        assert item.id == "IEC62531.2012Redline"
        assert item.abstract is not None


def test_create_bibitem_from_dict_yaml():
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "bib_item.yml")

    with open(file) as yaml_file:
        reference = yaml.safe_load(yaml_file)

        item = from_dict(reference)

        assert item is not None
        assert item.id == "ISOTC211"
        assert item.structuredidentifier is not None
