from Accuinsight.Lifecycle import keras
from Accuinsight.Lifecycle import tensorflow


class Lifecycle:
    """
    The exposed class to user
    """
    def __init__(self):
        self.accu_keras = keras.accuinsight()
        self.accu_tensorflow = tensorflow.accuinsight()

    def run_keras(self, tag=None):
        self.accu_keras.autolog(tag)

    def run_tensorflow(self, tag=None):
        self.accu_tensorflow.autolog(tag)
