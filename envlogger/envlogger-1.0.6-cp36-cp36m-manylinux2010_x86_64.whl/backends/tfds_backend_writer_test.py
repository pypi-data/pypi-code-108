# coding=utf-8
# Copyright 2022 DeepMind Technologies Limited..
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for tfds_backend_writer."""

import os
from typing import List

from absl.testing import absltest
import dm_env
from envlogger import step_data
from envlogger.backends import rlds_utils
from envlogger.backends import tfds_backend_testlib
from envlogger.backends import tfds_backend_writer
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds


def _create_step(value: int, step_type: dm_env.StepType) -> step_data.StepData:
  return step_data.StepData(
      action=value, timestep=dm_env.TimeStep(step_type, value, value, value))


def _tfds_features() -> tfds.features.FeaturesDict:
  return tfds.features.FeaturesDict({
      'steps':
          tfds.features.Dataset({
              'observation': tf.int64,
              'action': tf.int64,
              'reward': tf.int64,
              'is_terminal': tf.bool,
              'is_first': tf.bool,
              'is_last': tf.bool,
              'discount': tf.int64,
          }),
  })


class TfdsBackendWriterShardTest(absltest.TestCase):

  def test_add_episodes(self):
    temp_dir = self.create_tempdir()
    filepath = os.path.join(temp_dir.full_path, 'myfile')
    writer = tf.io.TFRecordWriter(os.fspath(filepath))
    shard = tfds_backend_writer.Shard(writer=writer)
    num_bytes = 0
    for i in range(2):
      record_bytes = tf.train.Example(
          features=tf.train.Features(feature={
              'intlist':
                  tf.train.Feature(int64_list=tf.train.Int64List(value=[i]))
          })).SerializeToString()
      shard.add_episode(record_bytes)
      num_bytes += len(record_bytes)
    shard.close_writer()

    self.assertEqual(shard.num_episodes, 2)
    self.assertEqual(shard.num_bytes, num_bytes)

    def _parse_example(ex):
      return tf.io.parse_single_example(
          ex, {'intlist': tf.io.FixedLenFeature([], dtype=tf.int64)})

    read_ds = tf.data.TFRecordDataset([filepath]).map(_parse_example)

    num_elements = 0
    for index, value in enumerate(read_ds):
      np.testing.assert_equal([index], value['intlist'])
      num_elements += 1
    self.assertEqual(num_elements, 2)


class TfdsBackendWriterEpisodeTest(absltest.TestCase):

  def test_add_step(self):
    episode = tfds_backend_writer.Episode(
        _create_step(0, dm_env.StepType.FIRST))
    step = _create_step(1, dm_env.StepType.MID)
    episode.add_step(step)

    self.assertEqual(episode.prev_step, step)
    self.assertLen(episode.steps, 1)

    expected_rlds_step = {
        'observation': 0,
        'action': 1,
        'reward': 1,
        'discount': 1,
        'is_first': True,
        'is_last': False,
        'is_terminal': False,
    }

    self.assertEqual(episode.steps[0], expected_rlds_step)

  def test_serialize_episode(self):
    episode = tfds_backend_writer.Episode(
        _create_step(0, dm_env.StepType.FIRST))
    episode.add_step(_create_step(1, dm_env.StepType.MID))
    episode.add_step(_create_step(2, dm_env.StepType.LAST))

    features = _tfds_features()
    serializer = tfds.core.example_serializer.ExampleSerializer(
        features.get_serialized_info())
    serialized_example = episode.serialize_episode(features, serializer)

    parser = tfds.core.example_parser.ExampleParser(
        features.get_serialized_info())
    episode = parser.parse_example(serialized_example)

    self.assertIsInstance(episode, dict)
    self.assertIn('steps', episode)

    steps = tf.data.Dataset.from_tensor_slices(episode['steps'])

    steps_counter = 0
    for index, step in enumerate(steps):
      self.assertEqual(index, step['observation'])
      self.assertFalse(step['is_terminal'])
      self.assertEqual(index == 0, step['is_first'])
      self.assertEqual(index == 2, step['is_last'])
      next_value = 0 if index == 2 else index + 1
      for key in ['action', 'reward', 'discount']:
        self.assertEqual(next_value, step[key])
      steps_counter += 1
    self.assertEqual(steps_counter, 3)


class TfdsBackendWriterSplitTest(absltest.TestCase):

  def test_update_split(self):
    split = tfds_backend_writer.Split(
        tfds.core.splits.SplitInfo(
            name='split_name', shard_lengths=[3], num_bytes=1))

    shard = tfds_backend_writer.Shard(writer=None, num_episodes=10, num_bytes=1)
    split.update(shard)

    self.assertEqual(split.complete_shards, 1)
    self.assertEqual(split.ds_name, 'rlds_envlogger_builder')
    self.assertEqual(split.info.name, 'split_name')
    self.assertEqual(split.info.shard_lengths, [3, 10])
    self.assertEqual(split.info.num_bytes, 2)

  def test_get_shard_path(self):
    split = tfds_backend_writer.Split(
        tfds.core.splits.SplitInfo(
            name='split_name', shard_lengths=[3], num_bytes=1),
        complete_shards=10)
    path = split.get_shard_path()

    self.assertEqual(path, 'rlds_envlogger_builder-split_name.tfrecord-00010')

  def test_get_split_dict(self):
    split_info = tfds.core.splits.SplitInfo(
        name='split_name', shard_lengths=[3], num_bytes=1)
    split = tfds_backend_writer.Split(split_info, complete_shards=10)
    split_dict = split.get_split_dict()

    self.assertEqual(split_dict['split_name'].num_examples,
                     split_info.num_examples)
    self.assertEqual(split_dict['split_name'].num_shards, split_info.num_shards)
    self.assertEqual(list(split_dict.keys()), ['split_name'])


class TfdsBackendWriterTest(absltest.TestCase):

  def _assert_steps(self, expected_steps: List[step_data.StepData],
                    steps: tf.data.Dataset):
    steps = steps.as_numpy_iterator()
    for idx, rlds_step in enumerate(steps):
      step = expected_steps[idx + 1] if idx < len(expected_steps) - 1 else None
      expected_step = rlds_utils.to_rlds_step(expected_steps[idx], step)
      np.testing.assert_equal(expected_step, rlds_step)

  def test_backend_writer(self):
    num_episodes = 5
    max_episodes_per_file = 3
    data_dir = self.create_tempdir(name='my_data_dir').full_path
    expected_episodes = tfds_backend_testlib.generate_episode_data(
        backend=tfds_backend_testlib.tfds_backend_catch_env(
            data_directory=data_dir,
            max_episodes_per_file=max_episodes_per_file),
        num_episodes=num_episodes)

    builder = tfds.core.builder_from_directory(data_dir)
    ds = builder.as_dataset(split='my_data_dir')

    num_episodes = 0
    for index, episode in enumerate(ds):
      self._assert_steps(expected_episodes[index], episode['steps'])
      self.assertEqual(episode['episode_id'], index)
      num_episodes += 1

    self.assertLen(expected_episodes, num_episodes)

  def test_backend_writer_with_split_name(self):
    num_episodes = 1
    max_episodes_per_file = 1
    data_dir = self.create_tempdir(name='my_data_dir').full_path
    expected_episodes = tfds_backend_testlib.generate_episode_data(
        backend=tfds_backend_testlib.tfds_backend_catch_env(
            data_directory=data_dir,
            max_episodes_per_file=max_episodes_per_file,
            split_name='split'),
        num_episodes=num_episodes)

    builder = tfds.core.builder_from_directory(data_dir)
    ds = builder.as_dataset(split='split')

    num_episodes = 0
    for index, episode in enumerate(ds):
      self._assert_steps(expected_episodes[index], episode['steps'])
      self.assertEqual(episode['episode_id'], index)
      num_episodes += 1

    self.assertLen(expected_episodes, num_episodes)


if __name__ == '__main__':
  absltest.main()
