from oarepo_taxonomies.utils import get_taxonomy_json

from oarepo_oai_pmh_harvester.decorators import post_processor


@post_processor(provider_parser_list=[
    {"provider": "nusl", "parser": "marcxml"},
    {"provider": "uk", "parser": "xoai"},
])
def call_add_date_defended(data):
    return add_date_defended(data)  # pragma: no cover


@post_processor(provider_parser_list=[
    {"provider": "nusl", "parser": "marcxml"},
    {"provider": "uk", "parser": "xoai"},
])
def call_add_defended(data):
    return add_defended(data)  # pragma: no cover


@post_processor("uk", "xoai")
def call_check_taxonomy(data):
    return check_taxonomy(data)


@post_processor("uk", "xoai")
def call_add_access_rights(data):
    return add_access_rights(data)


@post_processor(provider_parser_list=[
    {"provider": "nusl", "parser": "marcxml"},
    {"provider": "uk", "parser": "xoai"},
])
def call_add_item_relation_type(data):
    return add_item_relation_type(data)  # pragma: no cover


@post_processor("uk", "xoai")
def call_add_provider(data):
    return add_provider(data)


def add_administration(data):
    if "_administration" not in data:
        data["_administration"] = {
            "state": 'new',
            "primaryCommunity": "00216208",
            "communities": []
        }
    return data


@post_processor("uk", "xoai")
def call_add_administration(data):
    return add_administration(data)


def add_provider(data):
    ins_tax_dict = get_taxonomy_json(code="institutions", slug="00216208").paginated_data
    if "provider" not in data:
        data["provider"] = ins_tax_dict
    if "entities" not in data:
        data["entities"] = ins_tax_dict
    return data


def add_date_defended(data):
    resource_type = data.get("resourceType")
    resource_type = [_ for _ in resource_type if _["links"]["self"].split("/")[-1] == "theses-etds"]
    if len(resource_type) > 0 and "dateIssued" in data and "dateDefended" not in data:
        data["dateDefended"] = data.get("dateIssued", "")
    return data


def add_defended(data):
    resource_type = data.get("resourceType")
    resource_type = [_ for _ in resource_type if _["links"]["self"].split("/")[-1] == "theses-etds"]
    if len(resource_type) > 0:
        if not data.get("defended"):
            data["defended"] = True
    return data


def add_item_relation_type(data):
    if "relatedItem" not in data:
        return data
    resource_type = data.get("resourceType")
    resource_type = [_ for _ in resource_type if not _["is_ancestor"]]
    mapping = {
        "conference-papers": "isPartOf",
        "articles": "isPartOf",
        "conference-proceedings": "hasVersion",
        "books": "hasVersion",
        "conference-posters": "isPartOf",
        "research-reports": "isPartOf",

    }
    for _ in resource_type:
        link = _["links"]["self"]
        if link.endswith("/"):
            link = link.rstrip("/")
        slug = link.split("/")[-1]
        relation_type_slug = mapping.get(slug)
        if not relation_type_slug:
            return data
        else:
            taxonomy_json = get_taxonomy_json(code="itemRelationType",
                                              slug=relation_type_slug.lower()).paginated_data
            if taxonomy_json:
                for _ in data["relatedItem"]:
                    _["itemRelationType"] = taxonomy_json
            return data


def check_taxonomy(data):
    for k, v in data.items():
        if isinstance(v, list) and len([_ for _ in v if "links" in _]):
            data[k] = remove_duplicates(v)
    return data


def remove_duplicates(value: list):
    parents = set(
        [_.get("links", {}).get("parent") for _ in value if _.get("links", {}).get("parent")])
    new_value = []
    for _ in value:
        if not _["is_ancestor"]:
            if not _["links"]["self"] in parents:
                new_value.append(_)
        else:
            new_value.append(_)
    return new_value


def add_access_rights(data: dict):
    if 'accessRights' not in data:
        data['accessRights'] = get_taxonomy_json(code="accessRights", slug="c_abf2").paginated_data
    return data
