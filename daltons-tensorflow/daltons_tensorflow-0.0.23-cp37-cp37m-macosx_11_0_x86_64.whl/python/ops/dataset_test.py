import os
import socket
import tensorflow as tf
from threading import Thread
from pynng import Push0
from tensorflow.python.platform import test
from tensorflow.python.data.kernel_tests import test_base
from daltons_tensorflow.python.ops.dataset import DaltonsDataset, DaltonsTrainerDataset


current_dir = os.path.dirname(os.path.abspath(__file__))
path_to_test_file = os.path.abspath(current_dir + "/../../../../../testdata/test.tfrecord")

def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def _bytes_feature(value):
  """Returns a bytes_list from a string / byte."""
  if isinstance(value, type(tf.constant(0))):
    value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_feature(value):
  """Returns a float_list from a float / double."""
  return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
  """Returns an int64_list from a bool / enum / int / uint."""
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def serialize_example(action, context_feature, action_feature, reward, probability):
  """
  Creates a tf.Example message ready to be written to a file.
  """

  feature = {
      'action_id': _bytes_feature(action),
      'context_feature': _bytes_feature(context_feature),
      'action_feature': _bytes_feature(action_feature),
      'reward': _float_feature(reward),
      'probability': _float_feature(probability),
  }

  # Create a Features message using tf.train.Example.

  example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
  return example_proto.SerializeToString()

def send_examples(url):
    # Re-create server three times so dataset op needs to reconnect (validate that reconnecting works as expected)
    s1 = Push0()
    s1.listen(url)
    s1.send(serialize_example(b'action_1', b'context_feature_1', b'action_feature_1', 0, 0.5))
    s1.close()

    s1 = Push0()
    s1.listen(url)
    s1.send(serialize_example(b'action_2', b'context_feature_2', b'action_feature_2', 1, 0.5))
    s1.close()

    s1 = Push0()
    s1.listen(url)
    s1.send(serialize_example(b'action_3', b'context_feature_3', b'action_feature_3', 2, 0.5))
    s1.close()



class DaltonsDatasetTest(test_base.DatasetTestBase):
    def testDataset(self):
        with self.test_session():
            dataset = DaltonsDataset(
                "tfexample://{}".format(path_to_test_file) +
                "?context_feature_fields=context_feature" + 
                "&action_dependent_feature_fields=action_feature" + 
                "&reward_field=reward" + 
                "&action_id_field=action" + 
                "&probability_field=probability" + 
                "&default_probability=0.5",
            )

            def parse_example(example):
                return tf.io.parse_single_example(example, {
                    'action_feature': tf.io.FixedLenFeature([], tf.string),
                    'context_feature': tf.io.FixedLenFeature([], tf.string),
                    'action_id': tf.io.FixedLenFeature([], tf.string),
                    'reward': tf.io.FixedLenFeature([], tf.float32),
                    'probability': tf.io.FixedLenFeature([], tf.float32),
                })
            
            dataset = dataset.map(parse_example)

            self.assertDatasetProduces(dataset, [
                {'action_id': b'action_1', 'action_feature': b'action_feature_1', 'context_feature': b'context_feature_1', 'probability': 0.5, 'reward': 0.0},
                {'action_id': b'action_2', 'action_feature': b'action_feature_2', 'context_feature': b'context_feature_2', 'probability': 0.5, 'reward': 1.0},
                {'action_id': b'action_3', 'action_feature': b'action_feature_3', 'context_feature': b'context_feature_3', 'probability': 0.5, 'reward': 2.0},
            ])

    def testTrainerDataset(self):
        port = get_free_port()
        url = 'tcp://127.0.0.1:{}'.format(port)


        dataset = DaltonsTrainerDataset(url, retry_timeout=1000)
        def parse_example(example):
            return tf.io.parse_single_example(example, {
                'action_feature': tf.io.FixedLenFeature([], tf.string),
                'context_feature': tf.io.FixedLenFeature([], tf.string),
                'action_id': tf.io.FixedLenFeature([], tf.string),
                'reward': tf.io.FixedLenFeature([], tf.float32),
                'probability': tf.io.FixedLenFeature([], tf.float32),
            })
        
        dataset = dataset.map(parse_example).take(3)

        thread = Thread(target=send_examples, args=(url,))
        thread.start()

        self.assertDatasetProduces(dataset, [
            {'action_id': b'action_1', 'action_feature': b'action_feature_1', 'context_feature': b'context_feature_1', 'probability': 0.5, 'reward': 0.0},
            {'action_id': b'action_2', 'action_feature': b'action_feature_2', 'context_feature': b'context_feature_2', 'probability': 0.5, 'reward': 1.0},
            {'action_id': b'action_3', 'action_feature': b'action_feature_3', 'context_feature': b'context_feature_3', 'probability': 0.5, 'reward': 2.0},
        ])
        

if __name__ == "__main__":
    test.main()
