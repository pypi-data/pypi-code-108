# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.core import Workspace
from azureml.dataprep.api.functions import get_portable_path
from azureml.dataprep import col, get_stream_properties
from uuid import uuid4
from azureml.core import Datastore


def capture_file_layout(dataset_name, capture_extension_name=False):
    """Capture a dataset's file layout info and store it locally.

    :param dataset_name: The name of the dataset
    :type dataset_name: str
    :param capture_extension_name: whether to capture filename extension.
    :type capture_extension_name: bool
    """
    ws = Workspace.from_config()
    dataset = ws.datasets[dataset_name]
    output_file_name = str(uuid4()) + "_layout.txt"
    files_column = 'Path'
    PORTABLE_PATH = 'PortablePath'
    STREAM_PROPERTIES = 'StreamProperties'
    dataflow = dataset._dataflow \
        .add_column(get_portable_path(col(files_column), None), PORTABLE_PATH, files_column) \
        .add_column(get_stream_properties(col(files_column)), STREAM_PROPERTIES, PORTABLE_PATH) \
        .keep_columns([files_column, PORTABLE_PATH, STREAM_PROPERTIES])
    df = dataflow.to_pandas_dataframe(extended_types=True)
    folder_name_to_encrypted_name_dict = {}
    with open(output_file_name, "w", encoding="utf-8") as file:
        for i, row in df.iterrows():
            directory = row['PortablePath'].split("/")
            for index in range(0, len(directory)):
                folder_name = directory[index]
                if len(folder_name) > 0:
                    if folder_name not in folder_name_to_encrypted_name_dict:
                        folder_name_to_encrypted_name_dict[folder_name] = str(uuid4())
                    directory[index] = folder_name_to_encrypted_name_dict[folder_name]
                    if capture_extension_name and index == len(directory) - 1:
                        directory[index] = directory[index] + df[STREAM_PROPERTIES][i]['Extension']
            datastore_type = Datastore.get(ws, df[files_column][i].arguments["datastoreName"]).datastore_type
            file.write(datastore_type + " " + "/".join(directory) + " " + str(row['StreamProperties']['Size']) + "\n")

    print("layout captured in " + output_file_name)
