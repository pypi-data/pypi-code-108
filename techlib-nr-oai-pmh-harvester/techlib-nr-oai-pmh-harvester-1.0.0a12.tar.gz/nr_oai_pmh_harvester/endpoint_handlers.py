from oarepo_oai_pmh_harvester.decorators import endpoint_handler


@endpoint_handler(provider_parser_list=[
    {"provider": "nusl", "parser": "marcxml"},
    {"provider": "uk", "parser": "xoai"},
])
def call_nusl_handler(data):
    return nusl_handler(data)  # pragma: no cover


def nusl_handler(data):
    resource_type_array = data.get("resourceType")
    resource_type_array = [_ for _ in resource_type_array if _["is_ancestor"] is False]
    if len(resource_type_array) != 1:  # pragma: no cover
        raise Exception("Something unexpected happen, nusl should have one resource type")
    resource_type = resource_type_array[0]
    slug = resource_type["links"]["self"].split("/")[-1]
    return get_model_by_slug(slug)


def get_model_by_slug(slug):
    mapping = {
        "conference-materials": "events",
        "conference-papers": "events",
        "exhibition-catalogues-and-guides": "events",
        "business-trip-reports": "events",
        "press-releases": "events",
        'conference-proceedings': "events",
        "bachelor-theses": "theses",
        "master-theses": "theses",
        "rigorous-theses": "theses",
        "doctoral-theses": "theses",
        "post-doctoral-theses": "theses",
        "certified-methodologies": "nresults",
        "preservation-procedures": "nresults",
        "specialized-maps": "nresults",
    }
    return mapping.get(slug, "common") + "-community"
