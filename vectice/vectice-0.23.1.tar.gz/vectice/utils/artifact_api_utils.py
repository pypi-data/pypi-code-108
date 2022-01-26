import sys
from typing import Optional, Dict
from vectice.api.client import Client


def get_artifact_id(client: Client, artifact_name: str) -> Optional[int]:
    """
    Helper to get the dataset/model ID
    """
    try:
        artifact_type = str(sys._getframe(1).f_code.co_name)
        if "dataset" in artifact_type:
            return int(
                [
                    artifact.id
                    for artifact in client.list_datasets(artifact_name).list
                    if artifact.name == artifact_name
                ][0]
            )
        elif "model" in artifact_type:
            return int(
                [artifact.id for artifact in client.list_models(artifact_name).list if artifact.name == artifact_name][
                    0
                ]
            )
    except Exception as e:
        raise RuntimeError(f"The artifact ID wasn't found due to {e}")
    return None


def get_artifact_version_id(client: Client, artifact_id: int, version_number: int) -> Optional[int]:
    """
    Helper to get a dataset/model version id
    """
    try:
        artifact_type = str(sys._getframe(1).f_code.co_name)
        if "dataset" in artifact_type:
            return int(
                [
                    version
                    for version in client.list_dataset_versions(artifact_id).list
                    if version.versionNumber == version_number
                ][0].id
            )
        elif "model" in artifact_type:
            return int(
                [
                    version
                    for version in client.list_model_versions(artifact_id).list
                    if version.versionNumber == version_number
                ][0].id
            )
    except Exception as e:
        raise RuntimeError(f"The artifact version ID wasn't found due to {e}")
    return None


def update_artifact_properties(
    client: Client, artifact_id: int, artifact_version_id: int, artifact_model: Dict
) -> None:
    """
    Handles updating model version and dataset version properties
    """
    try:
        artifact_type = str(sys._getframe(1).f_code.co_name)
        if "dataset" in artifact_type:
            update_dataset_version_properties(client, artifact_id, artifact_version_id, artifact_model)
        elif "model" in artifact_type:
            update_model_version_properties(client, artifact_id, artifact_version_id, artifact_model)
    except Exception as e:
        raise RuntimeError(f"Updating properties was unsuccessful due to {e}")
    return None


def update_dataset_version_properties(
    client: Client, artifact_id: int, artifact_version_id: int, artifact_model: Dict
) -> None:
    old_properties = {
        old_prop.key: old_prop.id
        for old_prop in client.list_dataset_version_properties(artifact_id, artifact_version_id).list
    }
    for prop in artifact_model["properties"]:
        if prop.get("key") in old_properties.keys():
            prop["id"] = old_properties.get(prop["key"])
            client.update_dataset_version_properties(
                artifact_id, artifact_version_id, property_id=prop["id"], properties=prop
            )
        elif prop.get("key") not in old_properties.keys():
            client.create_dataset_version_properties(artifact_id, artifact_version_id, properties=prop)


# TODO not implemented yet
def update_model_version_properties(
    client: Client, artifact_id: int, artifact_version_id: int, artifact_model: Dict
) -> None:
    old_properties = {
        old_prop.key: old_prop.id
        for old_prop in client.list_model_version_properties(artifact_id, artifact_version_id).list
    }
    for prop in artifact_model["properties"]:
        if prop.get("key") in old_properties.keys():
            prop["id"] = old_properties.get(prop["key"])
            client.update_model_version_properties(  # type: ignore
                artifact_id, artifact_version_id, property_id=prop["id"], properties=prop
            )
        elif prop.get("key") not in old_properties.keys():
            client.create_model_version_properties(artifact_id, artifact_version_id, properties=prop)  # type: ignore
