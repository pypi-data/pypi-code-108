from pyspark.sql import *
from pyspark.sql.types import *
from pyspark.sql.functions import *

from .BaseSplitter import BaseSplitter

class SimpleSplitter(BaseSplitter):
  def __init__(self, options):
    super(SimpleSplitter, self).__init__(options)
    self.trainRatio = options.get("trainRatio", 0.8)
    self.random = options.get("random", True)
    self.randomSeed = options.get("randomSeed", 123)
    self.selectedFeatures = options.get("selectedFeatures", None)
    self.dateFeature = options.get("dateFeature", None)
    self.trainAll = options.get("trainAll", False)

  def split(self, data):
    if self.selectedFeatures is not None:
      data = data.select(self.selectedFeatures)

    if self.random:
      (training, test) = data.randomSplit([self.trainRatio, 1.0-self.trainRatio], self.randomSeed)
    elif self.dateFeature is not None:
      dfDates = data.dropDuplicates([self.dateFeature]).orderBy(desc(self.dateFeature))
      ndates = dfDates.count()
      trainDate = dfDates.limit(int(ndates*(1.0-self.trainRatio))).orderBy(self.dateFeature).first()[self.dateFeature]
      training = data.where(data[self.dateFeature] <= trainDate)
      test = data.where(data[self.dateFeature] > trainDate)
    else:
      return None, None

    if self.trainAll:
      return data, test

    return training, test
