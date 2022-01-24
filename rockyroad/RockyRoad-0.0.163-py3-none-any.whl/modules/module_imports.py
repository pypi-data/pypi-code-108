from uplink import (
    Consumer,
    get,
    post,
    patch,
    delete,
    returns,
    headers,
    Body,
    json,
    Query,
    Path,
    multipart,
    Part,
    PartMap,
)
from uplink import get as http_get
import os
from uuid import UUID


def get_key():

    try:
        key = os.environ["OCP_APIM_SUBSCRIPTION_KEY"]
    except KeyError as e:
        print(
            f"""ERROR: Define the environment variable {e} with your subscription key.  For example:

        export OCP_APIM_SUBSCRIPTION_KEY="INSERT_YOUR_SUBSCRIPTION_KEY"

        """
        )
        key = None
    return key


key = get_key()
