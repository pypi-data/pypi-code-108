from invenio_db import db
from marshmallow import ValidationError

from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer
from oarepo_taxonomies.utils import get_taxonomy_json
from sqlalchemy.exc import ProgrammingError

from nr_oai_pmh_harvester.query import get_query_by_slug


@rule("nusl", "marcxml", "/7112_", phase="pre")
def call_events(el, **kwargs):
    return events(el, **kwargs)


def events(el, **kwargs):
    res = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            res.append(get_event(_))
    if isinstance(el, dict):
        res = [get_event(el)]
    if res:
        return {"events": res}
    else:
        return OAITransformer.PROCESSED


def get_event(el):
    res = {}
    name = el.get("a")
    if name:
        res["nameOriginal"] = name
    alternate_name = el.get("g")
    if alternate_name:
        if isinstance(alternate_name, (tuple, list)):
            alternate_name = list(alternate_name)
        elif isinstance(alternate_name, str):
            alternate_name = [alternate_name]
        else:
            raise ValidationError(
                f"Bad format of alternate name: {alternate_name} is {type(alternate_name)}")
        res["nameAlternate"] = alternate_name
    date = el.get("d")
    if date:
        res["date"] = date
    place = el.get("c")
    if place:
        place = parse_place(place)
        if place:
            res["location"] = place
    return res


def parse_place(place: str):
    res = {}
    place_array = place.strip().rsplit("(", 1)
    country = place_array[-1].replace(")", "").strip().lower()
    place = place_array[0].strip()
    if place:
        res["place"] = place
    try:
        term = get_query_by_slug(taxonomy_code="countries", slug=country).one_or_none()
    except ProgrammingError:
        db.session.commit()
        return res
    if term:
        res["country"] = get_taxonomy_json(code="countries", slug=term.slug).paginated_data
    return res
