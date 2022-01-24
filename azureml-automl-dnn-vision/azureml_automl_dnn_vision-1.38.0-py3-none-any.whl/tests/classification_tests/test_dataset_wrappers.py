import pytest
import uuid

from typing import List

from azureml.automl.dnn.vision.classification.io.read.dataset_wrappers import ImageFolderDatasetWrapper, \
    ImageFolderLabelFileDatasetWrapper, AmlDatasetWrapper
from azureml.automl.dnn.vision.common.utils import _save_image_df
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper

from .aml_dataset_mock import AmlDatasetMock, WorkspaceMock, DataflowMock, DataflowStreamMock
import os
import pandas as pd


@pytest.mark.usefixtures('new_clean_dir')
class TestImageFolderDatasetWrapper:
    def test_generate_labels_files_from_imagefolder(self):
        dataset_wrapper = ImageFolderDatasetWrapper(
            'classification_data/image_folder_format')
        assert len(dataset_wrapper) == 4
        # check whether all images are in
        labels = []
        for _, label in dataset_wrapper:
            labels.append(label)

        assert len(set(labels)) == 2
        assert dataset_wrapper.num_classes == 2


@pytest.mark.usefixtures('new_clean_dir')
class TestImageFolderLabelFileDatasetWrapper:
    def test_get_labels(self):
        dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/binary_classification.csv',
            multilabel=True
        )
        assert len(dataset_wrapper) == 4
        labels = []
        for _, label in dataset_wrapper:
            labels.extend(label)

        assert len(set(labels)) == 2

    def test_valid_dataset(self):
        dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/binary_classification.csv',
            multilabel=True
        )

        valid_dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/valid_labels.csv',
            all_labels=dataset_wrapper.labels,
            multilabel=True
        )

        assert valid_dataset_wrapper.labels == dataset_wrapper.labels

    def test_labels_with_tabs(self):
        labels_file = str(uuid.uuid4())[:7] + '.txt'
        with open(labels_file, 'w') as fp:
            fp.write('crack_1.jpg\t"label_1\t"')

        dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file=labels_file
        )

        assert dataset_wrapper.labels == ['label_1\t']

    def test_labels_with_commas(self):
        labels_file = str(uuid.uuid4())[:7] + '.txt'
        with open(labels_file, 'w') as fp:
            fp.write('"crack_1.jpg"\t\'label_1,label_2\', label_3')

        dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file=labels_file,
            multilabel=True
        )

        assert set(dataset_wrapper.labels) == set(['label_1,label_2', 'label_3'])

    def test_missing_labels_in_validation(self):
        dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/binary_classification.csv',
            multilabel=True
        )

        valid_dataset_wrapper = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/invalid_labels.txt',
            all_labels=dataset_wrapper.labels,
            multilabel=True
        )

        assert set(dataset_wrapper.labels).issubset(set(valid_dataset_wrapper.labels))

        dataset_wrapper.reset_labels(valid_dataset_wrapper.labels)

        assert dataset_wrapper.labels == valid_dataset_wrapper.labels

    def test_bad_line_in_input_file(self):
        with pytest.raises(AutoMLVisionDataException):
            ImageFolderLabelFileDatasetWrapper(
                'classification_data/images',
                input_file='classification_data/multiclass_bad_line.csv',
                ignore_data_errors=False
            )

        dataset = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/multiclass_bad_line.csv',
            ignore_data_errors=True
        )

        assert len(dataset) == 3

    def test_missing_images_in_input_file(self):
        with pytest.raises(AutoMLVisionDataException):
            ImageFolderLabelFileDatasetWrapper(
                'classification_data/images',
                input_file='classification_data/multiclass_missing_image.csv',
                ignore_data_errors=False
            )

        dataset = ImageFolderLabelFileDatasetWrapper(
            'classification_data/images',
            input_file='classification_data/multiclass_missing_image.csv',
            ignore_data_errors=True
        )

        assert len(dataset) == 3


@pytest.mark.usefixtures('new_clean_dir')
class TestAmlDatasetDatasetWrapper:

    @staticmethod
    def _build_dataset(properties={},
                       image_column='image_url',
                       label_column='label',
                       number_of_files=2,
                       test_labels=['cat', 'dog'],
                       number_of_files_to_remove=0):
        test_dataset_id = 'd7c014ec-474a-49f4-8ae3-09049c701913'
        test_files = []
        for i in range(number_of_files):
            test_files.append('d7c014ec-474a-49f4-8ae3-09049c701913-{}.txt'.format(i))
        test_files_full_path = [os.path.join(AmlDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        label_dataset_data = {
            image_column: test_files,
            label_column: test_labels
        }

        files_subset = test_files_full_path[:len(test_files_full_path) - number_of_files_to_remove]
        labels_subset = test_labels[:len(test_labels) - number_of_files_to_remove]

        dataframe = pd.DataFrame(label_dataset_data)
        mockdataflowstream = DataflowStreamMock(files_subset)
        mockdataflow = DataflowMock(dataframe, mockdataflowstream, image_column)
        mockdataset = AmlDatasetMock(properties, mockdataflow, test_dataset_id)
        mockworkspace = WorkspaceMock(mockdataset)
        return mockworkspace, test_dataset_id, files_subset, labels_subset

    @staticmethod
    def _test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels,
                             multilabel=False, ignore_data_errors=False):
        try:
            datasetwrapper = AmlDatasetWrapper(test_dataset_id, workspace=mockworkspace, datasetclass=AmlDatasetMock,
                                               multilabel=multilabel, ignore_data_errors=ignore_data_errors)

            for i, test_label in enumerate(test_labels):
                assert datasetwrapper.label_at_index(i) == test_label, "Test label {}".format(i)

            labels = datasetwrapper.labels
            # flatten the test labels
            flatten_test_labels = []
            for label in test_labels:
                if isinstance(label, List):
                    flatten_test_labels += label
                else:
                    flatten_test_labels.append(label)
            assert set(flatten_test_labels) == set(labels), "Labels"
            assert datasetwrapper.multilabel == multilabel, "Multilabel"
            assert len(datasetwrapper) == len(test_files), "len"

            for test_file in test_files:
                assert os.path.exists(test_file)

        finally:
            for test_file in test_files:
                os.remove(test_file)

    def test_aml_dataset_wrapper_default(self):
        mockworkspace, test_dataset_id, test_files, test_labels = self._build_dataset()

        self._test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels)

    def test_aml_dataset_wrapper_properties(self):
        image_column = 'f'
        label_column = 'x'
        properties = {'_Image_Column:Image_': {'Column': image_column,
                                               'DetailsColumn': 'image_details'},
                      '_Label_Column:Label_': {'Column': label_column, 'Type': 'Classification'}}

        mockworkspace, test_dataset_id, test_files, test_labels = self._build_dataset(properties,
                                                                                      image_column,
                                                                                      label_column)

        self._test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels)

    def test_aml_dataset_wrapper_multilabel(self):
        test_label0 = ['cat', 'white']
        test_label1 = ['dog', 'black']
        mockworkspace, test_dataset_id, test_files, test_labels = self._build_dataset(
            test_labels=[test_label0, test_label1])

        self._test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels, multilabel=True)

    def test_aml_dataset_wrapper_with_some_multiclass_data(self):
        test_labels = [['cat', 'white'], 'horse', ['dog', 'black']]
        mockworkspace, test_dataset_id, test_files, test_labels = self._build_dataset(number_of_files=3,
                                                                                      test_labels=test_labels)

        # Item at index 1 should be removed by the dataset init.
        test_files = [file for index, file in enumerate(test_files) if index != 1]
        test_labels = [label for index, label in enumerate(test_labels) if index != 1]

        self._test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels,
                                  ignore_data_errors=True, multilabel=True)

    def test_aml_dataset_wrapper_multilabel_with_multiclass_dataset(self):
        mockworkspace, test_dataset_id, test_files, test_labels = self._build_dataset()

        with pytest.raises(AutoMLVisionDataException):
            self._test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels,
                                      ignore_data_errors=True, multilabel=True)

    def test_aml_dataset_wrapper_ignore_missing(self):
        mockworkspace, test_dataset_id, test_files, test_labels = \
            self._build_dataset(number_of_files_to_remove=1)

        self._test_datasetwrapper(mockworkspace, test_dataset_id, test_files, test_labels, ignore_data_errors=True)

    def test_aml_dataset_wrapper_train_test_split(self):
        mockworkspace, test_dataset_id, test_files, test_labels = self._build_dataset()

        try:
            datasetwrapper = AmlDatasetWrapper(test_dataset_id, workspace=mockworkspace, datasetclass=AmlDatasetMock)
            train_dataset_wrapper, valid_dataset_wrapper = datasetwrapper.train_val_split()
            _save_image_df(train_df=train_dataset_wrapper._images_df, val_df=valid_dataset_wrapper._images_df,
                           output_dir='.')

            if train_dataset_wrapper.labels != valid_dataset_wrapper.labels:
                all_labels = list(set(train_dataset_wrapper.labels + valid_dataset_wrapper.labels))
                train_dataset_wrapper.reset_labels(all_labels)
                valid_dataset_wrapper.reset_labels(all_labels)

            num_train_files = len(train_dataset_wrapper._CommonImageDatasetWrapper__files)
            num_valid_files = len(valid_dataset_wrapper._CommonImageDatasetWrapper__files)
            assert len(datasetwrapper._CommonImageDatasetWrapper__files) == num_train_files + num_valid_files
            assert sorted(datasetwrapper.labels) == sorted(all_labels)

            for test_file in test_files:
                assert os.path.exists(test_file)
            # it's train_df.csv and val_df.csv files created from _save_image_df function
            assert os.path.exists('train_df.csv')
            assert os.path.exists('val_df.csv')
        finally:
            for test_file in test_files:
                os.remove(test_file)
            os.remove('train_df.csv')
            os.remove('val_df.csv')
