from typing import Dict, Optional

from .context import get_context
from .core_api import safe_api_function


@safe_api_function("Creating model tags failed, error: {}")
def add_model_tags(model_id: str, tags: Dict[str, str]):
    """Adds or updates tags to an existing model.

    Each tag is a key:value pair, key and value must be strings.

    Args:
        model_id: Model ID
        tags: A mapping of tag keys to tag values

    Notes:
        * Each model is restricted to 10 tags
        * Tag keys are always converted to lowercase
        * If the `tags` parameter contains tag keys that were already
          defined for the model, their values will be updated.
    """
    context = get_context()
    context.event_loop.run_coroutine(
        context.http_client.post(url=f"/models/{model_id}/tags", data={"tags": tags})
    )


@safe_api_function("Deleting model tag failed, error: {}")
def delete_model_tag(model_id: str, tag_key: str):
    """Deletes a model tag.

    Args:
        model_id: Model ID
        tag_key: Tag key to delete

    Notes:
        * This function is best-effort, it will not fail if the tag doesn't exist.
    """
    context = get_context()
    context.event_loop.run_coroutine(
        context.http_client.delete(url=f"/models/{model_id}/tags/{tag_key}")
    )


@safe_api_function("Fetching model tags failed, error: {}")
def get_model_tags(model_id: str) -> Optional[Dict[str, str]]:
    """Fetches the tag keys and values of a model.

    Args:
        model_id: Model ID

    Returns:
        A dict mapping tag keys to values
    """
    context = get_context()
    return context.event_loop.run_coroutine(context.http_client.get(url=f"/models/{model_id}/tags"))
