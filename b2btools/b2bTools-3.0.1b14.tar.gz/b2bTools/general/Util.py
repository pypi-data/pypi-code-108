import bz2
import pickle as pickle

class Pickle:

  def __init__(self):
    pass

  def dump_data(self, filename, data):
    # compression 9 is default
    with bz2.BZ2File(filename, 'wb') as f:
      pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

  def load_data(self, filename):
    with bz2.BZ2File(filename, 'rb') as f:
      data = pickle.load(f, encoding='latin1')
      return data
    return None

