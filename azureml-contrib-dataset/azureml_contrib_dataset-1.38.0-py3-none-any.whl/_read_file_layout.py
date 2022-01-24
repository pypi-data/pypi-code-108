# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from azureml.core import Datastore
from azureml.core import Workspace
from azureml.data._dataprep_helper import dataprep


def _upload(src_path, datastore, root_location, glob_patterns=None, overwrite=True):
    destination = [datastore, root_location]
    engine_api = dataprep().api.engineapi.api.get_engine_api()
    dest_si = dataprep().api._datastore_helper._to_stream_info_value(destination[0], destination[1])
    glob_patterns = glob_patterns or None

    engine_api.upload_directory(
        dataprep().api.engineapi.typedefinitions.UploadDirectoryMessageArguments(
            base_path=src_path, destination=dest_si, folder_path=src_path, glob_patterns=glob_patterns,
            overwrite=overwrite
        )
    )


def _generate_fake_data(file_size, file_path, root_location):
    directory = file_path.split("/")
    directory.pop()
    Path(root_location + "/".join(directory)).mkdir(parents=True, exist_ok=True)
    with open(root_location + file_path, "w", encoding="utf-8") as file:
        for i in range(file_size):
            file.write("0")


def generate_repro_data(layout_file_name, root_location, blob_datastore_name=None, ADLS_gen1_datastore_name=None,
                        ADLS_gen2_datastore_name=None, file_share_datastore_name=None):
    """Reproduce a captured file layout.

    :param layout_file_name: The name of the layout file
    :type layout_file_name: str
    :param root_location: the destination folder for generated files
    :type root_location: str
    :param blob_datastore_name: the destination blob datastore
    :type blob_datastore_name: str
    :param ADLS_gen1_datastore_name: the destination ADLS gen1 datastore
    :type ADLS_gen1_datastore_name: str
    :param ADLS_gen2_datastore_name: the destination ADLS gen2 datastore
    :type ADLS_gen2_datastore_name: str
    :param file_share_datastore_name: the destination Azure File datastore
    :type file_share_datastore_name: str
    """

    AZURE_BLOB_TYPE = 'AzureBlob'
    ADLS_GEN1_TYPE = 'AzureDataLake'
    ADLS_GEN2_TYPE = 'AzureDataLakeGen2'
    AZURE_FILE_TYPE = "AzureFile"

    with open(layout_file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()

        for line in lines:
            file_layout = line.split(" ")
            if len(file_layout) == 3:
                if file_layout[0] == AZURE_BLOB_TYPE:
                    if not blob_datastore_name:
                        raise ValueError('missing blob datastore name')
                    _generate_fake_data(int(file_layout[2].rstrip()), file_layout[1], root_location
                                        + "/" + AZURE_BLOB_TYPE)
                elif file_layout[0] == ADLS_GEN1_TYPE:
                    if not ADLS_gen1_datastore_name:
                        raise ValueError('missing ADLS_gen1 datastore name')
                    _generate_fake_data(int(file_layout[2].rstrip()), file_layout[1], root_location
                                        + "/" + ADLS_GEN1_TYPE)
                elif file_layout[0] == ADLS_GEN2_TYPE:
                    if not ADLS_gen2_datastore_name:
                        raise ValueError('missing ADLS_gen2 datastore name')
                    _generate_fake_data(int(file_layout[2].rstrip()), file_layout[1], root_location
                                        + "/" + ADLS_GEN2_TYPE)
                elif file_layout[0] == AZURE_FILE_TYPE:
                    if not file_share_datastore_name:
                        raise ValueError('missing file share datastore name')
                    _generate_fake_data(int(file_layout[2].rstrip()), file_layout[1], root_location
                                        + "/" + AZURE_FILE_TYPE)
                else:
                    raise ValueError('missing or unsupported datastore type')
            else:
                raise ValueError('layout file is corrupted')
        print("layout reproduced")

    ws = Workspace.from_config()
    if blob_datastore_name:
        ds = Datastore.get(ws, blob_datastore_name)
        _upload(root_location + "/" + AZURE_BLOB_TYPE, ds, root_location)
        print("reproduced layout uploaded to " + blob_datastore_name)

    if ADLS_gen1_datastore_name:
        ds = Datastore.get(ws, ADLS_gen1_datastore_name)
        _upload(root_location + "/" + ADLS_GEN1_TYPE, ds, root_location)
        print("reproduced layout uploaded to " + ADLS_gen1_datastore_name)

    if ADLS_gen2_datastore_name:
        ds = Datastore.get(ws, ADLS_gen2_datastore_name)
        _upload(root_location + "/" + ADLS_GEN2_TYPE, ds, root_location)
        print("reproduced layout uploaded to " + ADLS_gen2_datastore_name)

    if file_share_datastore_name:
        ds = Datastore.get(ws, file_share_datastore_name)
        _upload(root_location + "/" + AZURE_FILE_TYPE, ds, root_location)
        print("reproduced layout uploaded to " + file_share_datastore_name)
