import os
from shutil import copyfile
import azureml.dataprep as dprep


class AmlDatasetMock:

    def __init__(self, properties, dataflow, id):
        self._properties = properties
        self._dataflow = dataflow
        self._id = id

    def download(self, stream_column, target_path=None, overwrite=False):
        self._dataflow.write_streams(stream_column, dprep.LocalFileOutput(target_path)).run_local()

    @staticmethod
    def get_by_id(workspace, id):
        assert id == workspace._ds._id, "Dataset Id"
        return workspace._ds


class WorkspaceMock:
    def __init__(self, ds):
        self._ds = ds


class DataflowMock:

    def __init__(self, pd, datastream, image_column):
        self._pd = pd
        self._datastream = datastream
        self._image_column = image_column

    def write_streams(self, column_name, local_file):
        return self._datastream

    def add_column(self, portable_path, portable_column_name, image_column_name):
        self._pd['PortablePath'] = self._pd[self._image_column]
        return self

    def to_pandas_dataframe(self, extended_types):
        assert extended_types, "extended_types isn't set"
        return self._pd


class DataflowStreamMock:

    def __init__(self, files_to_write):
        self._files_to_write = files_to_write

    def run_local(self):
        for file_path in self._files_to_write:
            copyfile(os.path.join(os.path.dirname(__file__),
                                  "../data/classification_data/images/crack_1.jpg"),
                     file_path)
