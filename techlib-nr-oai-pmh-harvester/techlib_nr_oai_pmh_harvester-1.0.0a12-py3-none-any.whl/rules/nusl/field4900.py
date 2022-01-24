from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("nusl", "marcxml", "/4900_", phase="pre")
def call_series(el, **kwargs):
    return series(el, **kwargs)  # pragma: no cover


def series(el, **kwargs):
    res = []
    if isinstance(el, dict):
        res.append(get_series(el))
    if isinstance(el, (tuple, list)):
        for _ in el:  # pragma: no cover
            res.append(get_series(_))
    if res:
        return {"series": res}
    else:
        return OAITransformer.PROCESSED  # pragma: no cover


def get_series(el):
    res = {}
    if title := el.get("a"):
        res["seriesTitle"] = title
    if volume := el.get("v"):
        res["seriesVolume"] = volume
    return res
