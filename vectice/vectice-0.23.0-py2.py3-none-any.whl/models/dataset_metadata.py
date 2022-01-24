from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple, Union
import re

from .with_properties import WithProperties
from .with_version import WithVersion
from .with_files_metadata import WithFilesMetadata
from .files_metadata import TreeItemType, TreeItem
from .data_resource_schema import DataResourceSchema, SchemaColumn, DataType
from .artifact import _Base


NOTEBOOK = {"ipynb": True}
IMAGE_FILE = {"png": True, "jpeg": True, "svg": True}


def schema_validation(description, max_length, precision, scale):
    return (
        description if description is not None else 0,
        max_length if max_length is not None else 0,
        precision if precision is not None else 0,
        scale if scale is not None else 0,
    )


def extract_table_data(table, table_name):
    schema_columns, type_check = [], None
    for schema in table.schema:
        data_type = str(schema.field_type).lower().capitalize()
        try:
            type_check = DataType[data_type].__dict__["_value_"]
        except KeyError:
            pass
        schema_description, schema_max_length, schema_precision, schema_scale = schema_validation(
            schema.description, schema.max_length, schema.precision, schema.scale
        )
        schema_columns += [
            SchemaColumn(
                name=schema.name,
                description=schema_description,
                dataType=type_check,
                length=schema_max_length,
                precision=schema_precision,
                scale=schema_scale,
            )
        ]
    data_resource_schema = DataResourceSchema(
        type=TreeItemType.DataTable,
        name=table_name,
        description="",
        fileFormat="bigquery#table",
        columns=schema_columns,
    )
    return data_resource_schema


def get_all_files_in_folder(client, database_name, project_id) -> Tuple[List[TreeItem], int]:
    from google.cloud.bigquery import DatasetReference

    files_size = 0
    children: List[TreeItem] = []
    tables = client.list_tables(database_name)

    for curr_table in tables:
        table_name = curr_table.table_id
        table_reference = DatasetReference(project_id, database_name).table(table_name)
        table = client.get_table(table_reference)
        data_resource_schema = extract_table_data(table, table_name)
        table_name, created, updated, size = table.table_id, table.created, table.modified, table.num_bytes
        files_size += size
        uri = f"bigquery://{project_id}/bigquery-public-data.{database_name}.{table_name}"
        children += [
            TreeItem(
                name=table_name,
                uri=uri,
                itemCreatedDate=created,
                itemUpdatedDate=updated,
                size=size,
                type=TreeItemType.DataTable,
                metadata=data_resource_schema,
            )
        ]

    return children, files_size


def extract_bigquery_metadata(uri: str) -> Optional[DatasetMetadata]:
    from google.cloud import bigquery
    from google.cloud.bigquery import DatasetReference

    try:
        match_table, match_dataset = re.search(r"&d=(.*?)&p=(.*?)&t=(.*?)&page", uri), re.search(
            r"&d=(.*?)&p=(.*?)&page", uri
        )
        if match_table:
            database_name, project_id, table_name = match_table.group(1), match_table.group(2), match_table.group(3)
            client = bigquery.Client(project=project_id)
            table_reference = DatasetReference(project_id, database_name).table(table_name)
            table = client.get_table(table_reference)
            data_resource_schema = extract_table_data(table, table_name)
            name, created, updated, size = table.table_id, table.created, table.modified, table.num_bytes
            uri = f"bigquery://{project_id}/bigquery-public-data.{database_name}.{table_name}"
            return DatasetMetadata().with_metadata(
                name=name,
                uri=uri,
                itemCreatedDate=created,
                itemUpdatedDate=updated,
                size=size,
                type=TreeItemType.DataTable,
                metadata=data_resource_schema,
            )
        elif match_dataset:
            database_name, project_id = match_dataset.group(1), match_dataset.group(2)
            client = bigquery.Client(project=project_id)
            children, files_size = get_all_files_in_folder(client, database_name, project_id)
            uri = f"bigquery://{database_name}"
            return DatasetMetadata().with_metadata(
                name=database_name, uri=uri, size=files_size, isFolder=True, children=children, type=TreeItemType.Folder
            )
    except Exception as e:
        raise RuntimeError(f"Big Query Dataset creation failed due to {e}")
    return None


# Searches entire tree *NB the same folder names cause clashes.
def search_tree(node, search):
    if node.name == search:
        return node
    elif node.children:
        for child in node.children:
            result = search_tree(child, search)
            if result:
                return result
    # Could not find the result in any of the children
    return None


# searches children instead of the entire tree -> No clashes with similar folder names and stays at correct depth of the tree
def search_tree_children(node, search):
    if node.name == search:
        return node
    elif node.children:
        for child in node.children:
            if child.name == search:
                return child
    # Could not find the result in any of the children
    return None


def decode_hash(blob):
    import base64
    import binascii

    # decode the hash provided
    base64_message = blob.md5_hash
    md5_hash = binascii.hexlify(base64.urlsafe_b64decode(base64_message))
    return md5_hash.decode("utf-8")


def get_file_type(file_name):
    file_type = file_name.split(".", 1)
    if "csv" == file_type[1].lower():
        return "CsvFile"
    elif NOTEBOOK.get(file_type[1].lower()):
        return "Notebook"
    elif IMAGE_FILE.get(file_type[1].lower()):
        return "ImageFile"
    elif "md" == file_type[1].lower():
        return "MdFile"
    else:
        return "File"


def attach_queue(branch, trunk, curr_blob=None, full_path=None, bucket_name=None):
    """
    Insert a branch of directories on its trunk. Trunk is the TreeItem
    """
    # splits dict to current file path and blob for metadata
    if isinstance(branch, dict):
        curr_blob = branch["blob"]
        parts = branch["name"].split("/", 1)
        full_path = f"{bucket_name}/{parts[0]}"
    else:
        parts = branch.split("/", 1)
        if full_path is not None:
            full_path = f"{full_path}/{parts[0]}"
    # splits file paths into partitions of 1
    if len(parts) == 1:  # branch is a file
        # if a single file is provided e.g file.csv // double check this
        if trunk.name is None:
            file_type = get_file_type(parts[0])
            (
                trunk.name,
                trunk.isFolder,
                trunk.digest,
                trunk.path,
                trunk.type,
                trunk.size,
                trunk.uri,
                trunk.itemCreatedDate,
            ) = (
                parts[0],
                False,
                decode_hash(curr_blob),
                f"gs://{full_path}",
                file_type,
                curr_blob.size,
                curr_blob.name,
                curr_blob.time_created,
            )
            return trunk
        # catches any unintentional blob errors e.g a file path with no file
        elif len(parts[0]) <= 0:
            return trunk
        file_type = get_file_type(parts[0])
        trunk.children += [
            TreeItem(
                name=parts[0],
                isFolder=False,
                digest=decode_hash(curr_blob),
                uri=f"gs://{bucket_name}/{curr_blob.name}",
                type=file_type,
                size=curr_blob.size,
                itemCreatedDate=curr_blob.time_created,
            )
        ]
    else:
        node, others = parts
        # Add the root information needed for the search
        if trunk.name is None:
            trunk.name, trunk.type, trunk.uri, trunk.isFolder = node, "Folder", f"gs://{full_path}", True
        # search tree if node is present
        search = search_tree_children(trunk, node)
        if search is not None:
            trunk = search
        elif search is None:
            # TODO Appends to top TreeItem for same level of directory e.g root is the last point of reference for the search // *Tree and not Forest*
            trunk.append(
                TreeItem(
                    name=node,
                    digest=decode_hash(curr_blob),
                    path=curr_blob.self_link,
                    isFolder=True,
                    type="Folder",
                    uri=f"gs://{full_path}",
                )
            )
            trunk = search_tree_children(trunk, node)
        # if it isn't present, continue adding sub folders
        attach_queue(others, trunk, curr_blob, full_path, bucket_name)


def extract_gcs_metadata(uri: Union[str, List[str]]) -> Optional[DatasetMetadata]:
    from google.cloud import storage

    storage_client = storage.Client()
    # Use a Forest for a list of uris
    forest = []
    if isinstance(uri, str):
        uri = [uri]

    for item in uri:

        match = re.search("(.*?)/(.*)", item)
        if match is None:
            logging.warning(f"Unable to parse {item}. Please ensure it follows the guidelines.")
            return None
        bucket_name, blob = match.group(1), match.group(2)

        # keep blobs so a single query is only used
        blobs_query = list(storage_client.list_blobs(bucket_name, prefix=blob))
        blobs = [{"name": blob.name, "blob": blob} for blob in blobs_query]
        if len(blobs) <= 0:
            raise ValueError(f"The file/folder '{item}' could not be found please check the uri.")
        # Assign a tree
        tree = TreeItem()

        for line in blobs:
            # catch files to avoid building directories
            if line["name"] == blob:

                parts = line["name"].split("/")
                file_type = get_file_type(parts[-1])
                (
                    tree.name,
                    tree.isFolder,
                    tree.digest,
                    tree.path,
                    tree.type,
                    tree.size,
                    tree.uri,
                    tree.itemCreatedDate,
                ) = (
                    parts[-1],
                    False,
                    decode_hash(line["blob"]),
                    f"gs://{line['name']}",
                    file_type,
                    line["blob"].size,
                    line["blob"].name,
                    line["blob"].time_created,
                )
            else:
                attach_queue(line, tree, bucket_name=bucket_name)
        forest += [tree]
    dataset = DatasetMetadata().with_metadata()
    dataset.filesMetadata = forest
    return dataset


# TODO Python 3.10 kw_only=true -> will allow for more flexible dataclass inheritance
@dataclass
class DatasetMetadata(_Base, WithVersion, WithProperties, WithFilesMetadata):
    autoVersion: bool = True

    @classmethod
    def create_bigquery(cls, uri: str) -> Optional[DatasetMetadata]:
        dataset_metadata_artifact = extract_bigquery_metadata(uri)
        return dataset_metadata_artifact

    @classmethod
    def create_gcs(cls, uri: Union[str, List[str]]) -> Optional[DatasetMetadata]:
        dataset_metadata_artifact = extract_gcs_metadata(uri)
        return dataset_metadata_artifact
