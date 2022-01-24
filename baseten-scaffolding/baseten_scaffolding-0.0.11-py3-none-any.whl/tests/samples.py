##############################################################################

PYTORCH_MODEL_CODE = """
import torch
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.main = torch.nn.Sequential(
            torch.nn.Linear(3, 1),
            torch.nn.Flatten(0, 1)
        )

    def forward(self, input):
        return self.main(input)
"""
with open('my_pytorch_model.py', 'w') as f:
    f.write(PYTORCH_MODEL_CODE)

from my_pytorch_model import MyModel
model = MyModel()

from baseten_scaffolding.scaffold.build import scaffold

ms = scaffold(model, model_files=['my_pytorch_model.py'], data_files=[], target_directory='test_pytorch')
ms.docker_build_string
ms.predict([[0,0,0]])


##############################################################################

from sklearn.ensemble import RandomForestClassifier
import random, string
random_suffix = ''.join([random.choice(string.ascii_letters) for _ in range(5)])
rfc = RandomForestClassifier()
from sklearn.datasets import load_iris
import pandas as pd
iris = load_iris()
feature_names = iris['feature_names']
class_labels = list(iris['target_names'])
data_x = iris['data']
data_y = iris['target']
data_x = pd.DataFrame(data_x, columns=feature_names)
rfc.fit(data_x, data_y)

from baseten_scaffolding.scaffold.build import scaffold
ms = scaffold(rfc, model_files=[], data_files=[])
ms.docker_build_string
ms.predict([[0,0,0,0]])

##############################################################################


EMBEDDING_REQUIREMENTS = """
tensorflow-hub==0.10.0
tensorflow==2.4.0
scikit-learn==0.23.2
"""

EMBEDDING_UTIL_CODE = """
import numpy as np


def get_top_k_indices(arr, k=5):
    return arr.argsort(axis=0)[-k::][::-1].tolist()


def create_reference_embeddings():
    random_fake_embeddings = np.random.randn(100,512)/10
    np.save('embeddings.npy', random_fake_embeddings)

"""

EMBEDDING_MODEL_CODE = """
import numpy as np
import tensorflow_hub as hub
from sklearn.metrics.pairwise import cosine_similarity
import pathlib

from embedding_util import get_top_k_indices

ENCODER_URL = 'https://tfhub.dev/google/universal-sentence-encoder/4'
REFERENCE_EMBED = 'embeddings.npy'


class MyEmbeddingModel:
    def __init__(self):
        self.embed = None
        self.reference_embeddings = None

    def load(self):
        self.embed = hub.load(ENCODER_URL)
        self.reference_embeddings = np.load(pathlib.Path('model', REFERENCE_EMBED).as_posix())

    def predict(self, inputs):
        # do the prediction
        embedding = self.embed(inputs)
        # compare the embedding with a reference dataset
        embedding_cosine_similarity = cosine_similarity(self.reference_embeddings, embedding)
        # find the most similar
        top_k_similar = get_top_k_indices(embedding_cosine_similarity)
        # return raw and processed results
        return {
            "embedding": embedding.numpy().tolist(),
            "top_k_similar": top_k_similar,
        }

"""
from pathlib import Path
path = Path('test_folder')
path.mkdir(parents=True, exist_ok=True)
# Create the model file
with open('test_folder/embedding_model.py', 'w') as f:
    f.write(EMBEDDING_MODEL_CODE)

# Create some utils file
with open('test_folder/embedding_util.py', 'w') as f:
    f.write(EMBEDDING_UTIL_CODE)

# Create the requirements file
with open('test_folder/embedding_reqs.txt', 'w') as f:
    f.write(EMBEDDING_REQUIREMENTS)

# Create a fake dataset to include with the deployment
from embedding_util import create_reference_embeddings
create_reference_embeddings()

from baseten_scaffolding.definitions.custom import CustomScaffoldDefinition
scaffold = CustomScaffoldDefinition(
    None,
    model_files=['test_folder/embedding_model.py', 'test_folder/embedding_util.py', 'embeddings.npy'],
    path_to_scaffold='test_custom',
    requirements_file='test_folder/embedding_reqs.txt',
    model_class='MyEmbeddingModel'
)
scaffold.predict(['hello world', 'bar baz'])

##############################################################################


import numpy as np
import pandas as pd

import tensorflow as tf

from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing

url = 'http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data'
column_names = ['MPG', 'Cylinders', 'Displacement', 'Horsepower', 'Weight',
                'Acceleration', 'Model Year', 'Origin']

raw_dataset = pd.read_csv(url, names=column_names,
                          na_values='?', comment='\t',
                          sep=' ', skipinitialspace=True)

dataset = raw_dataset.copy()
dataset.isna().sum()

dataset = dataset.dropna()
dataset['Origin'] = dataset['Origin'].map({1: 'USA', 2: 'Europe', 3: 'Japan'})
dataset = pd.get_dummies(dataset, columns=['Origin'], prefix='', prefix_sep='')

train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)

train_dataset.describe().transpose()

train_features = train_dataset.copy()
test_features = test_dataset.copy()

train_labels = train_features.pop('MPG')
test_labels = test_features.pop('MPG')

normalizer = preprocessing.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))

linear_model = tf.keras.Sequential([
    normalizer,
    layers.Dense(units=1)
])

linear_model.compile(
    optimizer=tf.optimizers.Adam(learning_rate=0.1),
    loss='mean_absolute_error'
)

history = linear_model.fit(
    train_features, train_labels,
    epochs=100,
    # suppress logging
    verbose=0,
    # Calculate validation results on 20% of the training data
    validation_split = 0.2
)

linear_model.predict(train_features[:10])

from baseten_scaffolding.definitions.keras import KerasScaffoldDefinition
scaffold = KerasScaffoldDefinition(linear_model)
scaffold.docker_build_string

scaffold.predict([[0,0,0,0,0,0,0,0,0]])

##############################################################################

from baseten_scaffolding.definitions.base import ReadModelScaffoldDefinition
x = ReadModelScaffoldDefinition('test_pytorch/')
x.predict([[0,0,0]])

##############################################################################
from baseten_scaffolding.definitions.huggingface_transformer import HuggingFaceTransformerPipelineScaffold

scaffold = HuggingFaceTransformerPipelineScaffold(model_type='text-generation', path_to_scaffold='test_hf')
