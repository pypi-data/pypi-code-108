import os

_html_template = os.path.realpath(__file__)
_html_template = _html_template.split("/")[:-1]
_html_template = "/".join(_html_template)
_html_template += "/template/{}.toml"
