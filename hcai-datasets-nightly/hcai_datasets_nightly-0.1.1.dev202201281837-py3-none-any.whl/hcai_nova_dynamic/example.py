import os
import hcai_datasets
import tensorflow_datasets as tfds

## Load Data
ds, ds_info = tfds.load(
  'hcai_nova_dynamic',
  split='dynamic_split',
  with_info=True,
  as_supervised=True,
  builder_kwargs={
    # Database Config
    'db_config_path': 'db.cfg',
    'db_config_dict': None,

    # Dataset Config
    'dataset': 'DFG_A1_A2b',
    'nova_data_dir': os.path.join('\\\\137.250.171.12', 'Korpora', 'nova', 'data'),
    'sessions': ['NP001'],
    'roles': ['caretaker', 'infant'],
    'schemes': ['IEng'],
    'annotator': 'gold',
    'data_streams': ['video.openpose[0,1,0]'],

    # Sample Config
    'frame_step': 5 / 25,
    'left_context': 0,
    'right_context': 0,
    'start': None,
    'end': None,
    # TODO: implement flatten samples and supervised keys
    'flatten_samples': False, # flag to determine wether multiples roles should be appeneded in sequence or added to one sample
    'supervised_keys': ['infant.video.openpose[0,1,0]', 'infant.IEng'], # flag to determine wether multiples roles should be appeneded in sequence or added to one sample

    # Additional Config
    'clear_cache' : False
  }
)

data_it = ds.as_numpy_iterator()
ex_data = next(data_it)
print(ex_data)