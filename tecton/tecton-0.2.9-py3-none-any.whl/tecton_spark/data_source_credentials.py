from typing import Optional
from typing import Tuple
from urllib.parse import urlparse


def get_kafka_secrets(
    ssl_keystore_location: str, ssl_keystore_password_secret_id: Optional[str] = None
) -> Tuple[str, Optional[str]]:

    local_keystore_password = None
    parsed_uri = urlparse(ssl_keystore_location, allow_fragments=False)

    if parsed_uri.scheme == "dbfs":
        path = parsed_uri.path.lstrip("/")
        local_keystore_loc = f"/dbfs/{path}"
    else:
        # This location must have been written to by a bootstrap script that copies the file from s3 to local.
        file_name = ssl_keystore_location.split("/")[-1]
        local_keystore_loc = f"/var/kafka-credentials/{file_name}"

    if ssl_keystore_password_secret_id:
        from tecton_spark import conf

        local_keystore_password = conf.get_or_none(ssl_keystore_password_secret_id)

    return local_keystore_loc, local_keystore_password
