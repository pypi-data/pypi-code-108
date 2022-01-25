import json

from datetime import date, datetime


class EyjaJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, (date, datetime)):
      return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
