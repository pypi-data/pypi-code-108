import requests
from typing import Any, Union, Iterable, Dict, List, Callable
from typing_extensions import Literal
from google.cloud import storage  # type: ignore
from http import HTTPStatus

# from .dataset import LabeledDataset

UrlCheckResult = Literal["SKIPPED", "FAILURE", "SUCCESS", "S3_PATH", "INVALID_URL"]


def check_urls(
    urls: Iterable[str],
    gs_client: Any,
    requesting_func: Callable[..., requests.Response] = requests.get,
) -> Dict[str, UrlCheckResult]:
    result = {}
    for url in urls:
        result[url] = check_url(url, gs_client, requesting_func=requesting_func)
    return result


def check_url(
    url: str,
    gs_client: Any,
    requesting_func: Callable[..., requests.Response] = requests.get,
) -> UrlCheckResult:
    if url.lower().startswith("gs://"):
        if gs_client is None:
            return "SKIPPED"
        else:
            bucket_name, path = url.replace("gs://", "").split("/", 1)
            try:
                bucket = gs_client.get_bucket(bucket_name)
                blob = bucket.get_blob(path)

                if blob is None:
                    return "FAILURE"
                else:
                    return "SUCCESS"
            except:
                return "FAILURE"
    elif url.lower().startswith("http"):
        try:
            # we use stream=True to avoid downloading the entire file for SSRF check
            with requesting_func(url, timeout=5, stream=True) as response:
                code = response.status_code
                if code == HTTPStatus.OK:
                    return "SUCCESS"
                else:
                    return "FAILURE"
        except:
            return "FAILURE"
    # We support S3 paths but only the user can access them from the app, and only if they provide their S3 creds
    # See client/src/util/bucketSigning.tsx
    elif url.lower().startswith("s3://"):
        return "S3_PATH"
    else:
        return "INVALID_URL"


UrlMode = Literal["ANONYMOUS", "INACCESSIBLE", "VALID", "INVALID_URL", "S3_PATH"]


def get_mode(
    urls: Iterable[str],
    local_results: Dict[str, UrlCheckResult],
    server_results: Dict[str, UrlCheckResult],
) -> Dict[str, UrlMode]:
    modes: Dict[str, UrlMode] = {}
    for url in urls:
        if server_results[url] == "FAILURE":
            if local_results[url] == "SUCCESS":
                modes[url] = "ANONYMOUS"
            elif local_results[url] == "SKIPPED":
                modes[url] = "INACCESSIBLE"
            elif local_results[url] == "FAILURE":
                modes[url] = "INACCESSIBLE"
        elif server_results[url] == "SUCCESS":
            modes[url] = "VALID"
        elif server_results[url] == "INVALID_URL":
            modes[url] = "INVALID_URL"
        elif server_results[url] == "S3_PATH":
            modes[url] = "S3_PATH"
    return modes


def get_errors(mode: Dict[str, UrlMode], dataset: Any) -> List[str]:
    errors = []

    is_anon = False
    for url in mode:
        if mode[url] == "INVALID_URL":
            errors += [
                f"{url} is not a supported URL format. Please provide a URL starting with gs://, s3://, http://, or https://"
            ]
        elif mode[url] == "INACCESSIBLE":
            errors += [
                f"{url} is not an accessible URL from Aquarium servers or this machine. Please verify the URL path."
            ]
        elif mode[url] == "S3_PATH":
            is_anon = True
            errors += [
                f"{url} is not an accessible URL from Aquarium servers. You will need to set your S3 creds in the web app to view your assets."
            ]
        elif mode[url] == "ANONYMOUS":
            is_anon = True

    if is_anon:
        if (
            len(dataset._temp_frame_embeddings_file_names) == 0
            and len(dataset._temp_frame_embeddings_file_names_streaming) == 0
        ):
            errors += [
                "Anonymous mode detected without embeddings. Please provide your own embeddings. Aquarium cannot compute embeddings in anonymous mode since images are inaccessible from the server."
            ]

    return errors
