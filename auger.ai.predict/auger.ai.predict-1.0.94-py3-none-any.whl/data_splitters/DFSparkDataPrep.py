
class DFSparkDataPrep(object):
  def __init__(self, options):
    self.options = options

  def _split(self, data, canSkipTargetFeature=False):
    targetFeature = self.options.get("targetFeature", None)
    selected_columns = self.options.get("featureColumns", []) + [targetFeature] + \
                       self.options.get("extraPredictColumns", [])

    if canSkipTargetFeature and targetFeature not in data.columns:
      selected_columns.remove(targetFeature)

    return data.select(selected_columns), None

  def split_training(self, data):
    return self._split(data)

  def split_predict(self, data):
    return self._split(data, True)

  def split_score(self, data):
    return self._split(data)
