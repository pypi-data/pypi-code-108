import json
from datetime import datetime


class QualityReportEncoder(json.JSONEncoder):
    """
    A JSON encoder for the quality report create->format interface
      which encodes datetimes as iso formatted strings.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return {"iso_date": obj.isoformat("T")}
        return super().default(obj)


class QualityValueEncoder(json.JSONEncoder):
    """
    A JSON encoder for the quality report distributed value storage -> report build interface.
      Currently, a placeholder for future serializations e.g. NaN,-Inf,+Inf
    """
