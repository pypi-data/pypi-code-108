import numpy as np

class TArrayData():
    @staticmethod
    def vec_to_array(c_vector):
        return np.array(c_vector.data())