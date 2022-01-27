"""hcai_nova_dynamic dataset."""

import numpy as np
import os
import shutil
import sys
import tensorflow_datasets as tfds
import tensorflow as tf

import hcai_datasets.hcai_nova_dynamic.utils.nova_types as nt
import hcai_datasets.hcai_nova_dynamic.utils.nova_data_utils as ndu
import hcai_datasets.hcai_nova_dynamic.utils.nova_anno_utils as nau

from hcai_datasets.hcai_nova_dynamic.utils.nova_data_utils import AudioData, VideoData, StreamData
from hcai_datasets.hcai_nova_dynamic.utils.nova_anno_utils import DiscreteAnnotation, ContinousAnnotation, FreeAnnotation

from hcai_datasets.hcai_nova_dynamic.nova_db_handler import NovaDBHandler
from hcai_datasets.hcai_nova_dynamic.utils.nova_utils import *

# TODO(hcai_audioset): Markdown description  that will appear on the catalog page.
_DESCRIPTION = """
The Nova Dynamic dataset can be used to retrieve the data and labels for a certain session or a certain part of a session of a nova dataset. 
This is part of the Nova CML Python backend (https://github.com/hcmlab/nova)
To specify which data to load use the following format: 

TODO: x
 
"""

# TODO(hcai_audioset): BibTeX citation
_CITATION = """
"""


class HcaiNovaDynamic(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for hcai_nova_dynamic dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
        '1.0.0': 'Initial release.',
    }

    def __init__(self, *, db_config_path=None, db_config_dict=None, dataset=None, nova_data_dir=None, sessions=None,
                 annotator=None,
                 schemes=None, roles=None, data_streams=None, start=None, end=None, left_context='0', right_context='0',
                 frame_size='1', stride=None,
                 flatten_samples=False, supervised_keys=None, clear_cache=True, add_rest_class=True, lazy_loading=False,
                 **kwargs):
        """
        Initialize the HcaiNovaDynamic dataset builder
        Args:
          nova_data_dir: the directory to look for data. same as the directory specified in the nova gui.
          frame_size: the framesize to look at. the matching annotation will be calculated as majority vote from all annotations that are overlapping with the timeframe.
          left_context: additional data to pass to the classifier on the left side of the frame.
          right_context: additional data to pass to the classifier on the left side of the frame.
          stride: how much a frame is moved to calculate the next sample. equals framesize by default.
          flatten_samples: if set to True samples with the same annotation scheme but from different roles will be treated as separate samples. only <scheme> is used for the keys.
          supervised_keys: if specified the dataset can be used with "as_supervised" set to True. Should be in the format <role>.<scheme>. if flatten_samples is true <role> will be ignored.
          clear_cache:  when set to True the cache will be cleared else the cached dataset will be used. make sure that dataset and sample config did not change. defaults to true.
          add_rest_class: when set to True an additional restclass will be added to the end the label list
          db_config_path: path to a configfile whith the nova database config.
          db_config_dict: dictionary with the nova database config. can be used instead of db_config_path. if both are specified db_config_dict is used.
          dataset: the name of the dataset. must match the dataset name in the nova database.
          sessions: list of sessions that should be loaded. must match the session names in nova.
          annotator: the name of the annotator that labeld the session. must match annotator names in nova.
          schemes: list of the annotation schemes to fetch
          roles: list of roles for which the annotation should be loaded.
          data_streams: list datastreams for which the annotation should be loaded. must match stream names in nova.
          start: optional start time_ms. use if only a specific chunk of a session should be retreived.
          end: optional end time_ms. use if only a specifc chunk of a session should be retreived.
          **kwargs: arguments that will be passed through to the dataset builder
        """
        self.dataset = dataset
        self.nova_data_dir = nova_data_dir
        self.sessions = sessions
        self.roles = roles
        self.schemes = schemes
        self.data_streams = data_streams
        self.annotator = annotator
        self.left_context_ms = ndu.parse_time_string_to_ms(left_context)
        self.right_context_ms = ndu.parse_time_string_to_ms(right_context)
        self.frame_size_ms = ndu.parse_time_string_to_ms(frame_size)
        self.stride_ms = ndu.parse_time_string_to_ms(stride) if stride else self.frame_size_ms
        self.start_ms = ndu.parse_time_string_to_ms(start) if start else 0
        self.end_ms = ndu.parse_time_string_to_ms(end) if end else float('inf')
        self.flatten_samples = flatten_samples
        self.clear_cache = clear_cache
        self.add_rest_class = add_rest_class
        self.lazy_loading = lazy_loading
        self.nova_db_handler = NovaDBHandler(db_config_path, db_config_dict)

        # Retrieving meta information from the database
        mongo_schemes = self.nova_db_handler.get_schemes(dataset=dataset, schemes=schemes)
        mongo_data = self.nova_db_handler.get_data_streams(dataset=dataset, data_streams=data_streams)
        self.label_info = self._populate_label_info_from_mongo_doc(mongo_schemes)
        self.data_info = self._populate_data_info_from_mongo_doc(mongo_data)

        # setting supervised keys
        if supervised_keys and self.flatten_samples:
            if supervised_keys[0] not in self.data_streams:
                # remove <role> of supervised keys
                _, data_stream = split_role_key(supervised_keys[0])
                if not data_stream in self.data_streams:
                    print('Warning: Cannot find supervised key \'{}\' in datastreams'.format(data_stream))
                    raise Warning('Unknown data_stream')
                else:
                    supervised_keys[0] = data_stream
            if supervised_keys[1] not in self.schemes:
                # remove <role> of supervised keys
                _, scheme = split_role_key(supervised_keys[1])
                if not scheme in schemes:
                    print('Warning: Cannot find supervised key \'{}\' in schemes'.format(scheme))
                    raise Warning('Unknown scheme')
                else:
                    supervised_keys[1] = scheme

        self.supervised_keys = tuple(supervised_keys) if supervised_keys else None

        super(HcaiNovaDynamic, self).__init__(**kwargs)

        if clear_cache:
            try:
                shutil.rmtree(self.data_dir)
            except OSError as e:
                print("Error: %s : %s" % (self.data_dir, e.strerror))

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""

        def map_label_id(lid):
            if self.flatten_samples and not lid == 'frame':
                return split_role_key(lid)[-1]
            return lid

        features_dict = {
                    # TODO: Remove frame when tfds implements option to disable shuffle
                    # Adding fake framenumber label for sorting
                    'frame': tf.string,
                    **{map_label_id(k): v.get_tf_info()[1] for k,v in self.label_info.items()},
                    **{map_label_id(k): v.get_tf_info()[1] for k, v in self.data_info.items()}
                }

        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            features=tfds.features.FeaturesDict(features_dict),
            supervised_keys= self.supervised_keys,
            homepage='https://github.com/hcmlab/nova',
            citation=_CITATION,
            disable_shuffling=True
        )

    def _populate_label_info_from_mongo_doc(self, mongo_schemes):
        """
        Setting self.label_info
        Args:
          mongo_schemes:

        Returns:

        """
        label_info = {}

        # List of all combinations from roles and schemes that occur in the retrieved data.
        for scheme in mongo_schemes:
            for role in self.roles:
                label_id = merge_role_key(role=role, key=scheme['name'])
                scheme_type = nt.string_to_enum(nt.AnnoTypes, scheme['type'])
                scheme_name = scheme['name']
                scheme_valid = scheme['isValid']

                if scheme_type == nt.AnnoTypes.DISCRETE:
                    labels = scheme['labels']
                    label_info[label_id] = nau.DiscreteAnnotation(role=role, add_rest_class=True, scheme=scheme_name, is_valid=scheme_valid, labels=labels)

                elif scheme_type == nt.AnnoTypes.DISCRETE_POLYGON:
                    labels = scheme['labels']
                    sr = scheme['sr']
                    label_info[label_id] = nau.DiscretePolygonAnnotation(role=role, scheme=scheme_name,
                                                                         is_valid=scheme_valid, labels=labels, sr=sr)

                elif scheme_type == nt.AnnoTypes.FREE:
                    label_info[label_id] = nau.FreeAnnotation(role=role, scheme=scheme_name, is_valid=scheme_valid)

                else:
                    raise ValueError('Invalid label type {}'.format(scheme['type']))

        return label_info

    def _populate_data_info_from_mongo_doc(self, mongo_data_streams):
        """
        Setting self.data
        Args:
          mongo_schemes:

        Returns:

        """
        data_info = {}

        for data_stream in mongo_data_streams:
            for role in self.roles:
                sample_stream_name = role + '.' + data_stream['name'] + '.' + data_stream['fileExt']
                sample_data_path = os.path.join(self.nova_data_dir, self.dataset, self.sessions[0], sample_stream_name)
                dtype = nt.string_to_enum(nt.DataTypes, data_stream['type'])

                if dtype == nt.DataTypes.VIDEO:
                    data = VideoData(role=role, name=data_stream['name'], file_ext=data_stream['fileExt'], sr=data_stream['sr'], is_valid=data_stream['isValid'], sample_data_path=sample_data_path)
                elif dtype == nt.DataTypes.AUDIO:
                    raise NotImplementedError('Audio files are not yet supported')
                elif dtype == nt.DataTypes.FEATURE:
                    data = StreamData(role=role, name=data_stream['name'], sr=data_stream['sr'], data_type=dtype, is_valid=data_stream['isValid'], sample_data_path=sample_data_path, lazy_loading=self.lazy_loading)
                else:
                    raise ValueError('Invalid data type {}'.format(data_stream['type']))

                data_id = merge_role_key(role=role, key=data_stream['name'])
                data_info[data_id] = data

        return data_info

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""
        return {'dynamic_split': self._generate_examples()}

    # def _get_data_for_frame(self, file_reader, feature_type, sr, start, end):
    #     start_frame = ndu.milli_seconds_to_frame(sr, start)
    #     end_frame = ndu.milli_seconds_to_frame(sr, end)
    #     if feature_type == nt.DataTypes.VIDEO:
    #         return ndu.chunk_vid(file_reader, start_frame, end_frame)
    #     elif feature_type == nt.DataTypes.AUDIO:
    #         raise NotImplementedError('Data chunking for audio is not yet implemented')
    #     elif feature_type == nt.DataTypes.FEATURE:
    #         return ndu.chunk_stream(file_reader, start_frame, end_frame)

    def _load_annotation_for_session(self, session, time_to_ms=False):
        for label_id, anno in self.label_info.items():
            mongo_anno = self.nova_db_handler.get_annos(self.dataset, anno.scheme, session, self.annotator, anno.role)
            anno.set_annotation_from_mongo_doc(mongo_anno, time_to_ms=time_to_ms)

    def _open_data_reader_for_session(self, session):
        for data_id, data in self.data_info.items():
            data_path = os.path.join(self.nova_data_dir, self.dataset, session, data_id + '.' + data.file_ext)
            data.open_file_reader(data_path)

    def _generate_examples(self):
            """Yields examples."""

            # Needed to sort the samples later and assure that the order is the same as in nova. Necessary for CML till the tfds can be returned in order.
            sample_counter = 1

            for session in self.sessions:

                # Gather all data we need for this session
                self._load_annotation_for_session(session, time_to_ms=True)
                self._open_data_reader_for_session(session)

                session_info = self.nova_db_handler.get_session_info(self.dataset, session)[0]
                dur = session_info['duration']
                # If are loading any datastreams we check if any datastream is shorter than the duration stored in the database suggests
                if self.data_info:
                    dur = int(min(*[v.dur for k,v in self.data_info.items()], dur ))

                if not dur:
                    raise ValueError('Session {} has no duration.'.format(session))

                dur_ms = dur * 1000

                # Starting position of the first frame in seconds
                c_pos_ms = self.left_context_ms + self.start_ms

                # Generate samples for this session
                while c_pos_ms + self.stride_ms + self.right_context_ms <= min(self.end_ms, dur_ms):
                    frame_start_ms = c_pos_ms - self.left_context_ms
                    frame_end_ms = c_pos_ms + self.frame_size_ms + self.right_context_ms
                    key = session + '_' + str(frame_start_ms / 1000) + '_' + str(frame_end_ms / 1000)

                    labels_for_frame = [{k: v.get_label_for_frame(frame_start_ms, frame_end_ms)} for k, v in self.label_info.items()]
                    data_for_frame = [{k: v.get_sample(frame_start_ms, frame_end_ms)} for k, v in self.data_info.items()]

                    sample_dict = {}

                    for l in labels_for_frame:
                        sample_dict.update(l)

                    for d in data_for_frame:
                        sample_dict.update(d)

                    if self.flatten_samples:

                        # grouping labels and data according to roles
                        for role in self.roles:

                            # filter dictionary to contain values for role
                            sample_dict_for_role = dict(filter(lambda elem: role in elem[0], sample_dict.items()))

                            # remove role from dictionary keys
                            sample_dict_for_role = dict(map(lambda elem: (elem[0].replace(role + '.', ''), elem[1]), sample_dict_for_role.items()))

                            sample_dict_for_role['frame'] = str(sample_counter) + '_' + key + '_' + role
                            #yield key + '_' + role, sample_dict_for_role
                            yield sample_counter, sample_dict_for_role
                            sample_counter += 1
                        c_pos_ms += self.stride_ms

                    else:
                        sample_dict['frame'] = str(sample_counter) + '_' + key
                        yield sample_counter, sample_dict
                        c_pos_ms += self.stride_ms
                        sample_counter += 1

                # closing file readers for this session
                for k,v in self.data_info.items():
                    v.close_file_reader()
