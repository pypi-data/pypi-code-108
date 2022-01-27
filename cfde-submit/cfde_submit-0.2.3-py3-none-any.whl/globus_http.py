import logging
import requests


logger = logging.getLogger(__name__)


def upload(data_path, destination_url, authorizer):
    """
    Arguments:
        data_path (str): The path to the data to ingest into DERIVA. The path can be:
                1) A directory to be formatted into a BDBag
                2) A Git repository to be copied into a BDBag
                3) A premade BDBag directory
                4) A premade BDBag in an archive file
        destination_url (str): The remote URL to use for uploading the data_path file
        authorizer (globus_sdk.AccessTokenAuthorizer): A valid Globus SDK authorizer
            with an access_token scoped for the Globus HTTPS server. NOTE:
            This differs between http servers, make sure you passed in the correct one!
    """
    headers = {}
    authorizer.set_authorization_header(headers)

    with open(data_path, 'rb') as bag_file:
        put_res = requests.put(destination_url, data=bag_file, headers=headers)

    # Regenerate headers on 401
    if put_res.status_code == 401:
        authorizer.handle_missing_authorization()
        authorizer.set_authorization_header(headers)
        with open(data_path, 'rb') as bag_file:
            put_res = requests.put(destination_url, data=bag_file, headers=headers)
    # Error message on failed PUT or any unexpected response
    if put_res.status_code >= 300:
        return {
            "success": False,
            "error": ("Could not upload BDBag to server (error {}):\n{}"
                      .format(put_res.status_code, put_res.content))
        }
    elif put_res.status_code != 200:
        logger.warning("Warning: HTTP upload returned status code {}, "
                       "which was unexpected.".format(put_res.status_code))

    logger.info("Upload successful to '{}': {} {}".format(destination_url, put_res.status_code,
                                                          put_res.content))
