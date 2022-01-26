from argparse import Namespace

import requests
from owl_client.utils import get_auth


def logs_pipeline(args: Namespace) -> None:
    """Cancel pipeline

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    schema = {True: "http", False: "https"}[args.insecure]
    headers = get_auth()
    url = "{}://{}/api/v1/pipeline/logs".format(schema, args.api)

    try:
        r = requests.get(url, params={"jobid": args.jobid}, headers=headers)
        print(r.text)
    except Exception as e:
        print("Failed to cancel pipeline: ", e)
