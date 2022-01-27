from collections import OrderedDict
from pathlib import Path

import torch
import pandas as pd
import numpy as np
from torch import nn
from torch.utils.data import Subset, DataLoader

from dnn_cool.collators.base import samples_to_dict_of_nested_lists, collate_nested_dict
from dnn_cool.converters.base import TypeGuesser
from dnn_cool.converters.full import Converters
from dnn_cool.converters.task.base import TaskConverter
from dnn_cool.converters.values.base import ValuesConverter
from dnn_cool.external.torch import TorchAutoGrad
from dnn_cool.synthetic_dataset.drawing_generators import generate_sample
from dnn_cool.synthetic_dataset.flows import body_regression, face_regression, person_regression, full_flow
from dnn_cool.synthetic_dataset.tokens_dataset import get_synthetic_token_classification_dataset
from dnn_cool.tasks.binary import BinaryClassificationTask
from dnn_cool.tasks.bounded_regression import BoundedRegressionTask
from dnn_cool.tasks.classification import ClassificationTask
from dnn_cool.tasks.development.binary import BinaryClassificationTaskForDevelopment
from dnn_cool.tasks.development.bounded_regression import BoundedRegressionTaskForDevelopment
from dnn_cool.tasks.development.classification import ClassificationTaskForDevelopment
from dnn_cool.tasks.development.multilabel_classification import MultilabelClassificationTaskForDevelopment
from dnn_cool.tasks.development.task_flow import TaskFlowForDevelopment
from dnn_cool.tasks.multilabel_classification import MultilabelClassificationTask
from dnn_cool.tasks.task_flow import TaskFlow, Tasks
from dnn_cool.utils.base import split_dataset, Values
from dnn_cool.value_converters import binary_value_converter, ImageCoordinatesValuesConverter, classification_converter, \
    MultiLabelValuesConverter


def create_df_and_images_tensor(n=int(1e4), cache_file=Path('dnn_cool_synthetic_dataset.pkl')):
    if cache_file.exists():
        return torch.load(cache_file)
    imgs = []
    rows = []
    names = []
    for i in range(n):
        img, row = generate_sample()
        imgs.append(torch.tensor(img).permute(2, 0, 1))
        rows.append(row)
        names.append(f'{i}.jpg')

    df = pd.DataFrame(rows)
    df['syn_img'] = names
    df.loc[:5, 'camera_blocked'] = np.nan
    res = torch.stack(imgs, dim=0).float() / 255., df
    torch.save(res, cache_file)
    return res


def get_synthetic_full_flow(n_shirt_types, n_facial_characteristics) -> TaskFlow:
    camera_blocked = BinaryClassificationTask('camera_blocked', nn.Linear(256, 1))
    door_open = BinaryClassificationTask('door_open', nn.Linear(256, 1))
    person_present = BinaryClassificationTask('person_present', nn.Linear(256, 1))
    face_x1 = BoundedRegressionTask('face_x1', nn.Linear(256, 1), 64)
    face_y1 = BoundedRegressionTask('face_y1', nn.Linear(256, 1), 64)
    face_w = BoundedRegressionTask('face_w', nn.Linear(256, 1), 64)
    face_h = BoundedRegressionTask('face_h', nn.Linear(256, 1), 64)
    facial_characteristics = MultilabelClassificationTask('facial_characteristics',
                                                          nn.Linear(256, n_facial_characteristics))
    body_x1 = BoundedRegressionTask('body_x1', nn.Linear(256, 1), 64)
    body_y1 = BoundedRegressionTask('body_y1', nn.Linear(256, 1), 64)
    body_w = BoundedRegressionTask('body_w', nn.Linear(256, 1), 64)
    body_h = BoundedRegressionTask('body_h', nn.Linear(256, 1), 64)
    shirt_type = ClassificationTask('shirt_type', nn.Linear(256, n_shirt_types))
    door_locked = BinaryClassificationTask('door_locked', nn.Linear(256, 1))
    leaf_tasks = [
        camera_blocked,
        door_open,
        person_present,
        face_x1, face_y1, face_w, face_h,
        facial_characteristics,
        body_x1, body_y1, body_w, body_h,
        shirt_type, door_locked
    ]
    tasks = Tasks(leaf_tasks, TorchAutoGrad())

    tasks.add_flow(body_regression)
    tasks.add_flow(face_regression)
    tasks.add_flow(person_regression)
    tasks.add_flow(full_flow)

    return tasks.get_full_flow()


class SecurityModule(nn.Module):

    def __init__(self, full_flow):
        super().__init__()
        self.seq = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 128, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.AvgPool2d(2),
            nn.Conv2d(128, 128, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, kernel_size=5),
            nn.AvgPool2d(2),
            nn.ReLU(inplace=True),
        )

        self.features_seq = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )

        self.face_localization_seq = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )

        self.body_localization_seq = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )

        self.flow_module = full_flow.torch()

    def forward(self, x):
        res = {}
        common = self.seq(x['syn_img'])
        res['features'] = self.features_seq(common)
        res['face_localization'] = self.face_localization_seq(common)
        res['body_localization'] = self.body_localization_seq(common)
        res['gt'] = x.get('gt')
        return self.flow_module(res)


def synthetic_dataset_preparation_without_converters(n=int(1e4)):
    imgs, df = create_df_and_images_tensor(n)
    full_flow = get_synthetic_full_flow(n_shirt_types=7, n_facial_characteristics=3)

    binary_classification_tasks = ['camera_blocked', 'door_open', 'person_present', 'door_locked']
    tasks_for_development = []
    for task_name in binary_classification_tasks:
        labels = binary_value_converter(df[task_name])
        tasks_for_development.append(BinaryClassificationTaskForDevelopment(task_name, labels))

    regression_tasks = [
        'face_x1', 'face_y1', 'face_w', 'face_h',
        'body_x1', 'body_y1', 'body_w', 'body_h'
    ]
    for task_name in regression_tasks:
        converter = ImageCoordinatesValuesConverter(dim=64)
        labels = converter(df[task_name])
        tasks_for_development.append(BoundedRegressionTaskForDevelopment(task_name, labels))

    labels = classification_converter(df['shirt_type'])
    tasks_for_development.append(ClassificationTaskForDevelopment('shirt_type', labels))

    multilabel_converter = MultiLabelValuesConverter()
    labels = multilabel_converter(df['facial_characteristics'])
    tasks_for_development.append(MultilabelClassificationTaskForDevelopment('facial_characteristics', labels))
    raise NotImplementedError()


def synthetic_dataset_preparation(n=int(1e4), perform_conversion=True):
    imgs, df = create_df_and_images_tensor(n)
    multilabel_converter = MultiLabelValuesConverter()
    n_shirt_types = classification_converter(df['person_regression.body_regression.shirt_type']).max().item() + 1
    n_facial_characteristics = \
        multilabel_converter(df['person_regression.face_regression.facial_characteristics']).shape[1]

    full_flow = get_synthetic_full_flow(n_shirt_types, n_facial_characteristics)

    output_col = ['camera_blocked', 'door_open', 'person_present', 'door_locked',
                  'person_regression.face_regression.face_x1',
                  'person_regression.face_regression.face_y1',
                  'person_regression.face_regression.face_w',
                  'person_regression.face_regression.face_h',
                  'person_regression.face_regression.facial_characteristics',
                  'person_regression.body_regression.body_x1',
                  'person_regression.body_regression.body_y1',
                  'person_regression.body_regression.body_w',
                  'person_regression.body_regression.body_h',
                  'person_regression.body_regression.shirt_type']
    type_guesser = TypeGuesser()
    type_guesser.type_mapping['camera_blocked'] = 'binary'
    type_guesser.type_mapping['door_open'] = 'binary'
    type_guesser.type_mapping['person_present'] = 'binary'
    type_guesser.type_mapping['door_locked'] = 'binary'
    type_guesser.type_mapping['person_regression.face_regression.face_x1'] = 'continuous'
    type_guesser.type_mapping['person_regression.face_regression.face_y1'] = 'continuous'
    type_guesser.type_mapping['person_regression.face_regression.face_w'] = 'continuous'
    type_guesser.type_mapping['person_regression.face_regression.face_h'] = 'continuous'
    type_guesser.type_mapping['person_regression.body_regression.body_x1'] = 'continuous'
    type_guesser.type_mapping['person_regression.body_regression.body_y1'] = 'continuous'
    type_guesser.type_mapping['person_regression.body_regression.body_w'] = 'continuous'
    type_guesser.type_mapping['person_regression.body_regression.body_h'] = 'continuous'
    type_guesser.type_mapping['syn_img'] = 'img'
    type_guesser.type_mapping['person_regression.body_regression.shirt_type'] = 'category'
    type_guesser.type_mapping['person_regression.face_regression.facial_characteristics'] = 'multilabel'

    values_converter = ValuesConverter()
    values_converter.type_mapping['img'] = lambda x: imgs
    values_converter.type_mapping['binary'] = binary_value_converter
    values_converter.type_mapping['continuous'] = ImageCoordinatesValuesConverter(dim=64)
    values_converter.type_mapping['category'] = classification_converter

    multilabel_converter = MultiLabelValuesConverter()
    values_converter.type_mapping['multilabel'] = multilabel_converter

    task_converter = TaskConverter()

    task_converter.type_mapping['binary'] = BinaryClassificationTaskForDevelopment
    task_converter.type_mapping['continuous'] = BoundedRegressionTaskForDevelopment
    task_converter.type_mapping['category'] = ClassificationTaskForDevelopment
    task_converter.type_mapping['multilabel'] = MultilabelClassificationTaskForDevelopment

    converters = Converters(project_dir=Path('./security_project'))
    converters.task = task_converter
    converters.type = type_guesser
    converters.values = values_converter

    full_flow_for_development = converters.create_task_flow_for_development(df, input_col='syn_img',
                                                                            output_col=output_col,
                                                                            task_flow=full_flow)

    dataset = full_flow_for_development.get_dataset()
    if perform_conversion:
        train_indices, val_indices = split_dataset(len(dataset), random_state=42)
        train_dataset = Subset(dataset, train_indices)
        val_dataset = Subset(dataset, val_indices)
        train_loader = DataLoader(train_dataset, batch_size=32 * torch.cuda.device_count(), shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=32 * torch.cuda.device_count(), shuffle=False)
        nested_loaders = OrderedDict({
            'train': train_loader,
            'valid': val_loader
        })
    else:
        nested_loaders = None
        train_dataset = None
        val_dataset = None

    model = SecurityModule(full_flow)
    datasets = {
        'train': train_dataset,
        'valid': val_dataset,
        'infer': val_dataset
    }
    children = full_flow_for_development.get_all_children()
    shirt_type = children['person_regression.body_regression.shirt_type']
    shirt_type.top_k = 10
    shirt_type.class_names = ['blue', 'red', 'yellow', 'cyan', 'magenta', 'green', 'black']
    children['person_regression.face_regression.facial_characteristics'].class_names = ['red', 'green', 'blue']
    return model, nested_loaders, datasets, full_flow_for_development, converters.tensorboard_converters


def get_synthetic_token_classification_flow():
    is_less_than_100 = BinaryClassificationTask('is_less_than_100', nn.Linear(16, 1))
    is_more_than_150 = BinaryClassificationTask('is_more_than_150', nn.Linear(16, 1))

    tasks = Tasks([is_less_than_100, is_more_than_150])

    @tasks.add_flow
    def full_flow(flow, x, out):
        out += flow.is_less_than_100(x.features)
        out += flow.is_more_than_150(x.features) | (~out.is_less_than_100)
        return out

    return tasks.get_full_flow()


def synthetic_token_classification():
    samples = get_synthetic_token_classification_dataset(1_00)
    full_flow = get_synthetic_token_classification_flow()
    is_less_than_100 = BinaryClassificationTaskForDevelopment(full_flow.get('is_less_than_100'),
                                                              samples['is_less_than_100'])
    is_more_than_150 = BinaryClassificationTaskForDevelopment(full_flow.get('is_more_than_150'),
                                                              samples['is_more_than_150'])

    values = Values(keys=['tokens'], types=['tokens'], values=[samples['tokens']])
    development_flow = TaskFlowForDevelopment(full_flow,
                                              values=values,
                                              tasks=[is_less_than_100, is_more_than_150])
    return development_flow


class TokenClassificationModel(nn.Module):

    def __init__(self, flow_module):
        super().__init__()
        self.flow_module = flow_module
        self.emb = nn.Sequential(
            nn.Embedding(num_embeddings=3, embedding_dim=64),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, 16),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.flow_module({
            'features': self.emb(x['tokens']),
            'gt': x.get('gt')
        })


def collate_token_classification(samples):
    data = samples_to_dict_of_nested_lists(samples)
    data.X_batch['tokens'] = collate_nested_dict(data.X_batch, ['tokens'],
                                                 shapes=data.X_shapes,
                                                 dtype=torch.long,
                                                 padding_value=0)
    data.X_batch['gt']['is_less_than_100'] = collate_nested_dict(data.X_batch,
                                                                 path=['gt', 'is_less_than_100'],
                                                                 shapes=data.X_shapes,
                                                                 dtype=torch.bool,
                                                                 padding_value=True)
    data.X_batch['gt']['_availability']['is_less_than_100'] = collate_nested_dict(data.X_batch,
                                                                                  path=['gt', '_availability',
                                                                                        'is_less_than_100'],
                                                                                  shapes=data.X_shapes,
                                                                                  dtype=torch.bool,
                                                                                  padding_value=False)
    data.X_batch['gt']['_availability']['is_more_than_150'] = collate_nested_dict(data.X_batch,
                                                                                  path=['gt', '_availability',
                                                                                        'is_more_than_150'],
                                                                                  shapes=data.X_shapes,
                                                                                  dtype=torch.bool,
                                                                                  padding_value=False)
    data.X_batch['gt']['_targets']['is_less_than_100'] = collate_nested_dict(data.X_batch,
                                                                             path=['gt', '_targets',
                                                                                   'is_less_than_100'],
                                                                             shapes=data.X_shapes,
                                                                             dtype=torch.bool,
                                                                             padding_value=False)
    data.X_batch['gt']['_targets']['is_more_than_150'] = collate_nested_dict(data.X_batch,
                                                                             path=['gt', '_targets',
                                                                                   'is_more_than_150'],
                                                                             shapes=data.X_shapes,
                                                                             dtype=torch.bool,
                                                                             padding_value=False)
    data.y_batch['is_less_than_100'] = collate_nested_dict(data.y_batch,
                                                           path=['is_less_than_100'],
                                                           shapes=data.y_shapes,
                                                           dtype=torch.float32,
                                                           padding_value=-1)
    data.y_batch['is_more_than_150'] = collate_nested_dict(data.y_batch,
                                                           path=['is_more_than_150'],
                                                           shapes=data.y_shapes,
                                                           dtype=torch.float32,
                                                           padding_value=-1)
    return data.X_batch, data.y_batch