import json
from urllib.request import urlopen

with urlopen('https://gitlab.com/huntsman-cancer-institute/risr/hea/hea-json-schemas/-/raw/master/wstlaction.json') as url:
    WSTL_ACTION_SCHEMA = json.loads(url.read().decode("utf-8"))

with urlopen('https://gitlab.com/huntsman-cancer-institute/risr/hea/hea-json-schemas/-/raw/master/wstl.json') as url:
    WSTL_SCHEMA = json.loads(url.read().decode("utf-8"))

with urlopen('https://gitlab.com/huntsman-cancer-institute/risr/hea/hea-json-schemas/-/raw/master/cjtemplate.json') as url:
    CJ_TEMPLATE_SCHEMA = json.loads(url.read().decode("utf-8"))

with urlopen('https://gitlab.com/huntsman-cancer-institute/risr/hea/hea-json-schemas/-/raw/master/nvpjson.json') as url:
    NVPJSON_SCHEMA = json.loads(url.read().decode("utf-8"))
