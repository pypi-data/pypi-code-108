# Standard library imports
import os
import zipfile
import json
import shutil

# Third party imports
import requests
import pandas as pd
import numpy as np

# Internal imports
from rohub import settings, utils, memo
from rohub.ResearchObject import ResearchObject
from rohub.Resource import Resource
from rohub._version import __version__


###############################################################################
#              Decorators.                                                    #
###############################################################################

def validate_authentication_token(func):
    def func_wrapper(*args, **kwargs):
        if utils.is_valid(token_type="access"):
            valid_token = True
        else:
            valid_token = utils.refresh_access_token()
        if valid_token:
            return func(*args, **kwargs)
    return func_wrapper


###############################################################################
#              Main Methods.                                                  #
###############################################################################

def login(username=None, password=None, client_id=None, client_secret=None):
    """
    | Function that handles access token generation and results in saving token information throughout the session.
    | There are two ways of authenticating:
    | 1) User authentication (username and password required)
    | 2) Client authentication (client_id and client_secret required)

    :param username: username for user authentication, optional
    :type username: str
    :param password: password for user authentication, optional
    :type password: str
    :param client_id: client id for client authentication, optional
    :type client_id: str
    :param client_secret: client secret for client authentication, optional
    :type client_secret: str
    :returns: None
    :rtype: None
    """
    url = settings.KEYCLOAK_URL
    if username and password:
        settings.USERNAME = username
        settings.PASSWORD = password
        data = {'client_id': settings.KEYCLOAK_CLIENT_ID,
                'client_secret': settings.KEYCLOAK_CLIENT_SECRET,
                'username': settings.USERNAME,
                'password': settings.PASSWORD,
                'grant_type': settings.GRANT_TYPE}
    elif client_id and client_secret:
        settings.KEYCLOAK_CLIENT_ID = client_id
        settings.KEYCLOAK_CLIENT_SECRET = client_secret
        settings.GRANT_TYPE = "client_credentials"
        settings.USERNAME = client_id
        data = {'client_id': settings.KEYCLOAK_CLIENT_ID,
                'client_secret': settings.KEYCLOAK_CLIENT_SECRET,
                'username': settings.USERNAME,
                'grant_type': settings.GRANT_TYPE}
    else:
        msg = "Incomplete input. To authenticate the user please provide username and password or" \
              " provide client_id and client_secret to authenticate using client!"
        raise SystemExit(msg)
    try:
        r = requests.post(url, data=data, timeout=settings.TIMEOUT)
        r.raise_for_status()
        r_json = r.json()
        settings.ACCESS_TOKEN = r_json.get('access_token')
        settings.ACCESS_TOKEN_VALID_TO = utils.valid_to(exp_time=r_json.get('expires_in'),
                                                        token_type="access token")
        settings.REFRESH_TOKEN = r_json.get('refresh_token')
        settings.REFRESH_TOKEN_VALID_TO = utils.valid_to(exp_time=r_json.get('refresh_expires_in'),
                                                         token_type="refresh token")
        settings.TOKEN_TYPE = r_json.get('token_type')
        settings.SESSION_STATE = r_json.get('session_state')
        print(f"Logged successfully as {settings.USERNAME}.")
    except requests.exceptions.HTTPError as e:
        print("Http error occurred.")
        print(e.response.text)
        raise e
    except requests.exceptions.ConnectionError:
        try:
            print("Connection error occurred. Trying again...")
            requests.post(url, data=data, timeout=settings.TIMEOUT)
        except requests.exceptions.ConnectionError as e:
            print("Connection error occurred for a second time. Aborting...")
            raise SystemExit(e.response.text)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    except requests.exceptions.Timeout as e:
        print("Timeout. Could not connect to the server.")
        raise SystemExit(e.response.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def whoami():
    """
    Function that returns service username for user that is currently logged in.

    :returns: username
    :rtype: str
    """
    if settings.USERNAME:
        return settings.USERNAME
    else:
        return "Currently not logged in!"


def version():
    """
    Displays the current package version.

    :returns: package version
    :rtype: str
    """
    return f"You are currently using package {__version__}."


def set_retries(number_of_retries):
    """
    Function that sets up maximum number of retries for validating a response status.

    .. note::
        You may want to increase number of retries or sleep time in case your job status
        validations ends up with information that there was not enough time to validate
        the status of the job. This can be dependent on current API traffic.

    :param number_of_retries: maximum number of retries
    :type number_of_retries: int
    :returns: None
    :rtype: None
    """
    if not isinstance(number_of_retries, int):
        print(f"number_of_retries has to be an integer, not {type(number_of_retries)}!")
    else:
        settings.RETRIES = number_of_retries
        print(f"number of retries is now changed to {settings.RETRIES}.")


def set_sleep_time(sleep_time):
    """
    Function that sets up sleep time for between requests for validating a response status.

    .. note::
        You may want to increase number of retries or sleep time in case your job status
        validations ends up with information that there was not enough time to validate
        the status of the job. This can be dependent on current API traffic.

    :param sleep_time: sleep time
    :type sleep_time: int
    :returns: None
    :rtype: None
    """
    if not isinstance(sleep_time, int):
        print(f"sleep_time has to be an integer, not {type(sleep_time)}!")
    else:
        settings.SLEEP_TIME = sleep_time
        print(f"sleep_time is now changed to {settings.SLEEP_TIME}.")


@validate_authentication_token
def show_my_user_profile_details():
    """
    Function that shows profile details for user that is currently logged in.

    :returns: response
    :rtype: dict
    """
    url = settings.API_URL + f"users/whoami/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def list_my_ros():
    """
    Function that lists research objects that belongs to the current user.

    :returns: table with listed research objects
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"search/ros/"
    params = {"owner": settings.USERNAME}
    r = utils.get_request_with_params(url=url, params=params)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    df = pd.DataFrame(results)
    if not df.empty:
        selected_columns = ['identifier', 'shared_link', 'title', 'description', 'created_on',
                            'created_by', 'modified_on', 'type', 'status', 'access_mode', 'owner',
                            'research_areas']
        df.drop(df.columns.difference(selected_columns), axis=1, inplace=True)
        column_sequence = ["identifier", "title", "description", "type", "research_areas",
                           "status", "created_on", "created_by", "modified_on", "access_mode",
                           "owner", "shared_link"]
        df = df.reindex(columns=column_sequence)
    return df


@validate_authentication_token
def is_job_success(job_id):
    """
    Function that checks the status of the job and validate if job succeed or not.

    :param job_id: job's identifier
    :type job_id: str
    :returns: response
    :rtype: dict
    """
    job_url = settings.API_URL + f"jobs/{job_id}/"
    job_r = utils.get_request(url=job_url, use_token=True)
    job_content = job_r.json()
    job_status = job_content['status']
    if job_status == "SUCCESS":
        return job_content
    elif job_status == "FAILURE":
        msg = f"Job failed with the following info: {job_content['output']}"
        raise SystemExit(msg)
    elif job_status == "WARNING":
        msg = f"Job succeeded but there is a following warning associated with it: {job_content['warnings']}"
        print(msg)
        return job_content
    else:
        print("Trying to confirm status of the job. It can take a while...")
        job_success = utils.check_for_status(job_url=job_url)
        if job_success:
            # updating response after success.
            job_r = utils.get_request(url=job_url, use_token=True)
            job_content = job_r.json()
            job_status = job_content['status']
            if job_status == "SUCCESS":
                return job_content
            elif job_status == "WARNING":
                msg = f"Job succeeded but there is a following warning associated with it: " \
                      f"{job_content['warnings']}"
                print(msg)
                return job_content
            else:
                msg = f"Job failed with the following info: {job_content['output']}"
                raise SystemExit(msg)
        else:
            msg = f"""Couldn't validate if uploading ended up with a success given the time limit.
                    You can try increasing retries through set_retries() and sleep time through 
                    set_sleep_time() functions and re-run it. You can also check if the current job
                    eventually succeeded by running is_job_success(job_id="{job_id}")"""
            raise SystemExit(msg)


###############################################################################
#              ROS main methods.                                              #
###############################################################################

@validate_authentication_token
def ros_find(search=None):
    """
    Function that finds a specific research object against provided query.

    :param search: phrase to search against, optional
    :type search: str
    :returns: table containing selected information about the research object/objects
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"search/ros/"
    if search:
        params = {"search": search}
        r = utils.get_request_with_params(url=url, params=params)
    else:
        r = utils.get_request(url=url)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    df = pd.DataFrame(results)
    if not df.empty:
        selected_columns = ['identifier', 'shared_link', 'title', 'description', 'created_on',
                            'created_by', 'modified_on', 'type', 'status', 'access_mode', 'owner',
                            'research_areas']
        df.drop(df.columns.difference(selected_columns), axis=1, inplace=True)
        column_sequence = ["identifier", "title", "description", "type", "research_areas",
                           "status", "created_on", "created_by", "modified_on", "access_mode",
                           "owner", "shared_link"]
        df = df.reindex(columns=column_sequence)
    return df


@validate_authentication_token
def ros_search_using_id(identifier):
    """
    Function that finds research object based on its identifier.

    :param identifier: research object identifier
    :type identifier: str
    :returns: response containing details for the research object
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


def ros_create(title, research_areas, description=None, access_mode=None,
               ros_type=None, use_template=False, owner=None, editors=None,
               readers=None, creation_mode=None):
    """
    Function that creates new Research Object in the API and instantiates a Python object that can be reused.

    .. seealso::
        | :func:`~list_valid_research_areas`
        | :func:`~list_valid_access_modes`
        | :func:`~list_valid_ros_types`
        | :func:`~list_valid_templates`
        | :func:`~list_valid_creation_modes`

    .. note::
        The newly created research object will return a Python object that has its own set of methods
        and attributes. You may want to assign it to a variable to make it easy to work with.
        For example: ``my_ros = ros_create(**your set of params)``

    :param title: title of your research object
    :type title: str
    :param research_areas: research areas associated with your research object
    :type research_areas: list
    :param description: description of your research object, optional
    :type description: str
    :param access_mode: research object's access mode, optional
    :type access_mode: str
    :param ros_type: research object's type, optional
    :type ros_type: str
    :param use_template: if True appropriate template for ro type will be used, optional
    :type use_template: bool
    :param owner: research object's owner, optional
    :type owner: str
    :param editors: research object's editors, optional
    :type editors: list
    :param readers: research object's readers, optional
    :type readers: list
    :param creation_mode: research object's creation mode, optional
    :type creation_mode: str
    :returns: newly created research object
    :rtype: ResearchObject
    """
    return ResearchObject.ResearchObject(title=title, research_areas=research_areas,
                                         description=description, access_mode=access_mode,
                                         ros_type=ros_type, use_template=use_template, owner=owner,
                                         editors=editors, readers=readers, creation_mode=creation_mode,
                                         post_request=True)


def ros_load(identifier):
    """
    Function that loads an existing research object.

    :param identifier: str -> research object's identifier
    :type identifier: str
    :returns: loaded research object
    :rtype: ResearchObject
    """
    return ResearchObject.ResearchObject(identifier=identifier, post_request=False)


@validate_authentication_token
def ros_content(identifier):
    """
    Function that retrieves research object's content based on its identifier.

    :param identifier: str -> research object's identifier
    :type identifier: str
    :returns: response containing details for research object's content
    :rtype: dict
    """
    if utils.is_valid(token_type="access"):
        url = settings.API_URL + f"ros/{identifier}/content/"
        r = utils.get_request(url=url, use_token=True)
        content = r.json()
        return content
    else:
        msg = "Your current access token is either missing or expired, please log into" \
              " rohub again"
        raise SystemExit(msg)


@validate_authentication_token
def ros_full_metadata(identifier):
    """
    Function that retrieves research object's full metadata based on identifier.

    :param identifier: str -> research object's identifier
    :type identifier: str
    :returns: response containing details for research object's content
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/full/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def ros_fork(identifier, title=None, description=None):
    """
    Function that creates research object's fork.

    :param identifier: str -> research object's identifier
    :type identifier: str
    :param title: fork title, optional
    :type title: str
    :param description: fork description, optional
    :type description: str
    :returns: fork identifier
    :rtype: str
    """
    url = settings.API_URL + f"ros/{identifier}/evolution/"
    data = {"status": "FORK",
            "title": title,
            "description": description}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    job_id = content["identifier"]
    if job_id:
        fork_response = is_job_success(job_id=job_id)
        forked_results = fork_response.get("results")
        if forked_results:
            forked_ros_id = forked_results.split("/")[-2]
            return forked_ros_id
    else:
        msg = "Incorrect job response, couldn't validate if file was uploaded or not."
        raise SystemExit(msg)


@validate_authentication_token
def ros_snapshot(identifier, title=None, description=None, create_doi=None,
                 external_doi=None, publication_services=None):
    """
    Function that creates research object's snapshot.

    .. seealso::
        :func:`~list_valid_publication_services`

    .. note::
        if one chooses to use doi it can be provided in two ways:
        1) through setting create_doi to True, then doi will be generated for you
        2) through passing your doi using external_doi parameter
        create_doi = True and external_doi are mutually exclusive, therefore
        they can't be used simultaneously!

    .. warning::
        user needs to make sure that he has service credentials associated with his profile
        for the publication services that he would like to use!
        If that is not the case, warning will be shown and the ros will not be published as intended!

    :param identifier: str -> research object's identifier
    :type identifier: str
    :param title: snapshot title, optional
    :type title: str
    :param description: snapshot description, optional
    :type description: str
    :param create_doi: doi is created if True, False otherwise, optional, False is the default
    :type create_doi: bool
    :param external_doi: existing doi value that will be associated with the snapshot, optional
    :type external_doi: str
    :param publication_services: services where the snapshot should be published into
    :type publication_services: list
    :returns: snapshot identifier
    :rtype: str
    """
    if create_doi:
        if not isinstance(create_doi, bool):
            msg = f"create_doi parameter has to be a boolean type, not a {type(create_doi)}"
            raise SystemExit(msg)
        if external_doi:
            msg = "Illegal usage: create_doi=True and external_doi are mutually exclusive!"
            raise SystemExit(msg)
    if publication_services:
        validated = []
        try:
            available_services = set(list_valid_publication_services())
            for candidate in publication_services:
                validated.extend(utils.validate_against_different_formats(input_value=candidate,
                                                                          valid_value_set=available_services))
            if validated:
                publication_services = validated
            else:
                publication_services = None
        except KeyError as e:
            print(f"Couldn't validate publication_services value! Omitting this parameter.")
            print(e)
            publication_services = None
    url = settings.API_URL + f"ros/{identifier}/evolution/"
    data = {"status": "SNAPSHOT",
            "title": title,
            "description": description,
            "create_doi": create_doi,
            "external_doi": external_doi,
            "publication_services": publication_services}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    job_id = content["identifier"]
    if job_id:
        snapshot_response = is_job_success(job_id=job_id)
        snapshot_results = snapshot_response.get("results")
        if snapshot_results:
            snapshot_ros_id = snapshot_results.split("/")[-2]
            return snapshot_ros_id
    else:
        msg = "Incorrect job response, couldn't validate if file was uploaded or not."
        raise SystemExit(msg)


@validate_authentication_token
def ros_archive(identifier, title=None, description=None, create_doi=None,
                external_doi=None, publication_services=None):
    """
    Function that creates research object's archive.

    .. seealso::
        :func:`~list_valid_publication_services`

    .. note::
        if one chooses to use doi it can be provided in two ways:
        1) through setting create_doi to True, then doi will be generated for you
        2) through passing your doi using external_doi parameter
        create_doi = True and external_doi are mutually exclusive, therefore
        they can't be used simultaneously!

    .. warning::
        user needs to make sure that he has service credentials associated with his profile
        for the publication services that he would like to use!
        If that is not the case, warning will be shown and the ros will not be published as intended!

    :param identifier: str -> research object's identifier
    :type identifier: str
    :param title: archive title, optional
    :type title: str
    :param description: archive description, optional
    :type description: str
    :param create_doi: doi is created if True, False otherwise, optional, False is the default
    :type create_doi: bool
    :param external_doi: existing doi value that will be associated with the snapshot, optional
    :type external_doi: str
    :param publication_services: services where the archive should be published into
    :type publication_services: list
    :returns: archive identifier
    :rtype: str
    """
    if create_doi:
        if not isinstance(create_doi, bool):
            msg = f"create_doi parameter has to be a boolean type, not a {type(create_doi)}"
            raise SystemExit(msg)
        if external_doi:
            msg = "Illegal usage: create_doi=True and external_doi are mutually exclusive!"
            raise SystemExit(msg)
    if publication_services:
        validated = []
        try:
            available_services = set(list_valid_publication_services())
            for candidate in publication_services:
                validated.extend(utils.validate_against_different_formats(input_value=candidate,
                                                                          valid_value_set=available_services))
            if validated:
                publication_services = validated
            else:
                publication_services = None
        except KeyError as e:
            print(f"Couldn't validate publication_services value! Omitting this parameter.")
            print(e)
            publication_services = None
    url = settings.API_URL + f"ros/{identifier}/evolution/"
    data = {"status": "ARCHIVE",
            "title": title,
            "description": description,
            "create_doi": create_doi,
            "external_doi": external_doi,
            "publication_services": publication_services}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    job_id = content["identifier"]
    if job_id:
        archive_response = is_job_success(job_id=job_id)
        archive_results = archive_response.get("results")
        if archive_results:
            archive_ros_id = archive_results.split("/")[-2]
            return archive_ros_id
    else:
        msg = "Incorrect job response, couldn't validate if file was uploaded or not."
        raise SystemExit(msg)


def ros_list_publications(identifier):
    """
    Function that lists publication details related to specific research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :return: set of selected information regarding each publication
    :rtype: list
    """
    url = settings.API_URL + f"ros/{identifier}/publications/"
    r = utils.get_request(url=url, use_token=False)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    publications = []
    for result in results:
        publications.append({"doi": result.get("doi"),
                             "storage": result.get("storage"),
                             "storage_record_id": result.get("storage_record_identifier")})
    return publications


def ros_triple_details(identifier):
    """
    Function that shows details for triple based on it's identifier.

    :param identifier: triple's identifier
    :type identifier: str
    :returns: response containing triple details
    :rtype: dict
    """
    url = settings.API_URL + f"triples/{identifier}"
    r = utils.get_request(url=url, use_token=False)
    content = r.json()
    return content


@validate_authentication_token
def ros_list_annotations(identifier):
    """
    Function that lists all annotations associated with specific research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :return: set of selected information regarding each annotation
    :rtype: list
    """
    url = settings.API_URL + f"ros/{identifier}/annotations/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    annotations = []
    for result in results:
        annotations.append({"identifier": result.get("identifier"),
                            "name": result.get("name"),
                            "filename": result.get("filename"),
                            "created": result.get("created"),
                            "creator": result.get("creator")})
    return annotations


@validate_authentication_token
def ros_list_triples(identifier):
    """
    Function that lists all triples related to a specific annotation.

    :param identifier: annotation's identifier
    :type identifier: str
    :return: set of selected information regarding each triple
    :rtype: list
    """
    url = settings.API_URL + f"annotations/{identifier}/body/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    triples = []
    for result in results:
        triples.append({"identifier": result.get("identifier"),
                        "subject": result.get("subject"),
                        "predicate": result.get("predicate"),
                        "object": result.get("object"),
                        "created_by": result.get("created_by"),
                        "created_on": result.get("created_on")})
    return triples


@validate_authentication_token
def ros_list_authors(identifier):
    """
    Function that lists authors associated with certain research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: response containing authors details
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/authors/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def ros_list_contributors(identifier):
    """
    Function that lists contributors associated with certain research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: response containing contributors details
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/contributors/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def ros_list_copyright(identifier):
    """
    Function that lists copyrights associated with certain research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: response containing copyright details
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/copyright/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def ros_list_fundings(identifier):
    """
    Function that lists fundings associated with certain research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: table containing selected information about funding
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"ros/{identifier}/fundings/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    df = pd.DataFrame(content.get("results"))
    if not df.empty:
        try:
            df_a = pd.json_normalize(df["grant"])   # exploding grant part to df
            df_a.rename(columns={"identifier": "grant_id", "name": "grant_name", "title": "grant_title"},
                        inplace=True)
            df_b = pd.json_normalize(df["funder"])   # exploding funder part to df
            df_b.rename(columns={"type": "funder_type", "doi": "funder_doi", "name": "funder_name"}, inplace=True)
            df.drop(["grant", "funder"], axis=1, inplace=True)   # those are no longer needed
            df.rename(columns={"identifier": "funding_id", "type": "funding_type"}, inplace=True)
            df = df.join([df_a, df_b])
        # in case anything goes wrong lets return original dataframe with results
        except Exception:
            pass
    return df


@validate_authentication_token
def ros_list_license(identifier):
    """
    Function that lists license associated with certain research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: response containing license details
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/license/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def ros_list_resources(identifier):
    """
    Function that lists resources associated with specific research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: table containing selected information about all associated resources
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"ros/{identifier}/resources/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    df = pd.DataFrame(results)
    if not df.empty:
        selected_columns = ["identifier", "type", "title", "description", "url", "name",
                            "path", "size", "creator", "created_on", "modified_on", "download_url"]
        df.drop(df.columns.difference(selected_columns), axis=1, inplace=True)
        df["source"] = np.where(df["url"].isna(), "internal", "external")
        column_sequence = ["identifier", "type", "source", "title", "description", "url", "name",
                           "path", "size", "creator", "created_on", "modified_on", "download_url"]
        df = df.reindex(columns=column_sequence)
    return df


@validate_authentication_token
def ros_list_folders(identifier):
    """
    Function that lists folders associated with specific research object.

    :param identifier: research object's identifier.
    :type identifier: str
    :returns: table containing selected information about all associated folders
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"ros/{identifier}/folders/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    df = pd.DataFrame(results)
    if not df.empty:
        selected_columns = ["identifier", "name", "description", "path", "creator",
                            "created_on", "modified_on"]
        df.drop(df.columns.difference(selected_columns), axis=1, inplace=True)
    return df


@validate_authentication_token
def ros_export_to_rocrate(identifier, filename=None, path=None, use_format=settings.EXPORT_TO_ROCRATE_DEFAULT_FORMAT):
    """
    Function for downloading research object's metadata as RO-crate.

    :param identifier: research object's identifier
    :type identifier: str
    :param filename: plain filename without extension, optional - if not provided username will be used instead
    :type filename: str
    :param path: folder path to where file should be downloaded, optional - default is current working directory
    :type path: str
    :param use_format: format choice for acquired data - either json-ld or zip
    :type use_format: str
    :returns: None
    :rtype: None
    """
    if not filename:
        filename = settings.USERNAME
    if path:
        os.makedirs(path, exist_ok=True)
        full_path = os.path.join(path, filename)
    else:
        full_path = os.path.join(filename)
    url = settings.API_URL + f"ros/{identifier}/crate/download/"
    if use_format == "json-ld":
        r = utils.get_file_request(url=url, use_token=True)
        with open(f'{full_path}.jsonld', 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)
        del r
        if path:
            print(f"File was successfully downloaded into {path}.")
        else:
            print(f"File was successfully downloaded.")
    elif use_format == "zip":
        r = utils.get_file_request(url=url, use_token=True, application_type="application/zip")
        with open(f'{full_path}.zip', 'wb') as out_file:
            out_file.write(r.content)
        del r
        if path:
            print(f"File was successfully downloaded into {path}.")
        else:
            print(f"File was successfully downloaded.")
    else:
        print(f"Incorrect use_format. Has to be one of: json-ld, zip. Instead {use_format} was passed.")


###############################################################################
#              ROS add methods.                                               #
###############################################################################


@validate_authentication_token
def ros_add_geolocation(identifier, body_specification_json=None):
    """
    Function that adds geolocation to a specific research object.

    :param identifier: research object's id
    :type identifier: str
    :param body_specification_json: path to the JSON file or Python serializable object (dict, list), optional
    :type body_specification_json: str/dict/list
    :returns: response content from the API
    :rtype: dict
    """
    if body_specification_json:
        if isinstance(body_specification_json, str):
            if os.path.isfile(body_specification_json):
                file = open(body_specification_json)
                body_specification_json = file.read()
        elif isinstance(body_specification_json, (dict, list)):
            body_specification_json = json.dumps(body_specification_json)
        else:
            print(f"Unexpected type of body_specification_json parameter. {type(body_specification_json)} was passed and"
                  f" string (path to file) or dictionary was expected!. Leaving body_specification_json value empty.")
            body_specification_json = None
    url = settings.API_URL + f"ros/{identifier}/geolocation/"
    data = {"ro": identifier,
            "body_specification_json": body_specification_json}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_add_folders(identifier, name, description=None, parent_folder=None):
    """
    Function that adds folders to the specific research object.

    :param identifier: research's object identifier
    :type identifier: str
    :param name: folder's name
    :type name: str
    :param description: folder's description, optional
    :type description: str
    :param parent_folder: parent folder identifier, optional
    :type parent_folder: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/folders/"
    data = {"ro": identifier,
            "name": name,
            "description": description,
            "parent_folder": parent_folder}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_add_annotations(identifier, resources=None, body_specification_json=None):
    """
    Function that adds annotations to the specific research object.

    :param identifier: research object's identifier
    :type identifier: str
    :param resources: resources to which annotations will be applied, optional
    :type resources: list
    :param body_specification_json: path to the JSON file or Python serializable object (dict, list), optional
    :type body_specification_json: str/dict/list
    :returns: response content from the API
    :rtype: dict
    """
    if body_specification_json:
        if isinstance(body_specification_json, str):
            if os.path.isfile(body_specification_json):
                file = open(body_specification_json)
                body_specification_json = file.read()
        elif isinstance(body_specification_json, (dict, list)):
            body_specification_json = json.dumps(body_specification_json)
        else:
            print(f"Unexpected type of body_specification_json parameter. {type(body_specification_json)} was passed and"
                  f" string (path to file) or dictionary was expected!. Leaving body_specification_json value empty.")
            body_specification_json = None
    url = settings.API_URL + f"ros/{identifier}/annotations/"
    data = {"ro": identifier,
            "resources": resources,
            "body_specification_json": body_specification_json}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


def ros_add_internal_resource(identifier, res_type, file_path, title=None, folder=None, description=None):
    """
    Function that adds internal resource to the specific research object.

    .. seealso::
        :func:`~list_valid_resource_types`

    .. note::
        The newly created resource object will return a Python object that has its own set of methods
        and attributes. You may want to assign it to a variable to make it easy to work with.
        For example: ``my_res = ros_add_internal_resource(**your set of params)``

    :param identifier: research object's identifier
    :type identifier: str
    :param res_type: type of resource
    :type res_type: str
    :param file_path: resource's file path
    :type file_path: str
    :param title: resource's title, optional
    :type title: str
    :param folder: folder's identifier, optional
    :type folder: str
    :param description: resource's description
    :type description: str
    :returns: newly created resource object
    :rtype: Resource
    """
    return Resource.Resource(ro_id=identifier, source="internal", resource_type=res_type,
                             file_path=file_path, title=title, folder=folder, description=description,
                             post_request=True)


def ros_add_external_resource(identifier, res_type, input_url, title=None, folder=None, description=None):
    """
    Function that adds external resource to the specific research object.

    .. seealso::
        :func:`~list_valid_resource_types`

    .. note::
        The newly created resource object will return a Python object that has its own set of methods
        and attributes. You may want to assign it to a variable to make it easy to work with.
        For example: ``my_res = ros_add_external_resource(**your set of params)``

    :param identifier: research object's identifier
    :type identifier: str
    :param res_type: type of resource
    :type res_type: str
    :param input_url: resource's url
    :type input_url: str
    :param title: resource's title, optional
    :type title: str
    :param folder: folder's identifier, optional
    :type folder: str
    :param description: resource's description
    :type description: str
    :returns: newly created resource object
    :rtype: Resource
    """
    return Resource.Resource(ro_id=identifier, source="external", resource_type=res_type,
                             input_url=input_url, title=title, folder=folder, description=description,
                             post_request=True)


@validate_authentication_token
def ros_add_triple(the_subject, the_predicate, the_object, annotation_id, object_class=None):
    """
    Function that adds triple to the specific annotation.

    .. seealso::
        :func:`~list_triple_object_classes`

    :param the_subject: triple's subject
    :type the_subject: str
    :param the_predicate: triple's predicate
    :type the_predicate: str
    :param the_object: triple's object
    :type the_object: str
    :param annotation_id: annotation's identifier
    :type annotation_id: str
    :param object_class: object's class, optional
    :type object_class: str
    :returns: response content from the API
    :rtype: dict
    """
    if object_class:
        try:
            valid_object_classes = list_triple_object_classes()
            verified_object_classes = utils.validate_against_different_formats(input_value=object_class,
                                                                               valid_value_set=valid_object_classes)
            # checking if set contains at least one element
            if len(verified_object_classes):
                # expected behaviour, only one value is correct
                object_class = verified_object_classes[0]
            else:
                # else leaving it empty
                object_class = None
        except Exception as e:
            msg = f"Couldn't validate object_class value! Leaving it empty!"
            print(msg)
            print(e)
            object_class = None
    url = settings.API_URL + "triples/"
    data = {"subject": the_subject,
            "predicate": the_predicate,
            "object": the_object,
            "object_class": object_class,
            "annotation": annotation_id}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_set_authors(identifier, agents):
    """
    Function that sets authors to a specific research object.

    :param identifier: research object's identifier
    :type identifier: str
    :param agents: usernames representing authors, if one doesn't exist it will be automatically created
    :type agents: list
    :returns: response content from the API
    :rtype: dict
    """
    if not isinstance(agents, list):
        msg = f"agents parameter has to be a list type, not a {type(agents)}"
        raise SystemExit(msg)
    validated_agents = utils.list_validated_agents(agents=agents, allow_org=False)
    if not validated_agents:
        msg = "At least one valid agent has to be provided!"
        raise SystemExit(msg)
    url = settings.API_URL + f"ros/{identifier}/authors/"
    data = {"ro": identifier,
            "agents": validated_agents}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_set_contributors(identifier, agents):
    """
    Function that sets contributor to a specific research object.

    :param identifier: research object's identifier
    :type identifier: str
    :param agents: usernames representing contributors, if one doesn't exist it will be automatically created
    :type agents: list
    :returns: response content from the API
    :rtype: dict
    """
    if not isinstance(agents, list):
        msg = f"agents parameter has to be a list type, not a {type(agents)}"
        raise SystemExit(msg)
    validated_agents = utils.list_validated_agents(agents=agents, allow_org=False)
    if not validated_agents:
        msg = "At least one valid agent has to be provided!"
        raise SystemExit(msg)
    if not isinstance(agents, list):
        msg = f"agents parameter has to be a list type, not a {type(agents)}"
        raise SystemExit(msg)
    url = settings.API_URL + f"ros/{identifier}/contributors/"
    data = {"ro": identifier,
            "agents": validated_agents}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_set_publishers(identifier, agents):
    """
    Function that sets publishers to a specific research object.

    :param identifier: research object's identifier
    :type identifier: str
    :param agents: usernames/organizations representing publishers, if one doesn't exist it will be automatically created
    :type agents: list
    :returns: response content from the API
    :rtype: dict
    """
    if not isinstance(agents, list):
        msg = f"agents parameter has to be a list type, not a {type(agents)}"
        raise SystemExit(msg)
    validated_agents = utils.list_validated_agents(agents=agents, allow_org=True)
    if not validated_agents:
        msg = "At least one valid agent has to be provided!"
        raise SystemExit(msg)
    url = settings.API_URL + f"ros/{identifier}/publisher/"
    data = {"ro": identifier,
            "agents": validated_agents}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_set_copyright_holders(identifier, agents):
    """
    Function that sets copyright holders to a specific Research Object.

    :param identifier: research object's identifier
    :type identifier: str
    :param agents: usernames/organizations representing holders, if one doesn't exist it will be automatically created
    :type agents: list
    :returns: response content from the API
    :rtype: dict
    """
    if not isinstance(agents, list):
        msg = f"agents parameter has to be a list type, not a {type(agents)}"
        raise SystemExit(msg)
    validated_agents = utils.list_validated_agents(agents=agents, allow_org=True)
    if not validated_agents:
        msg = "At least one valid agent has to be provided!"
        raise SystemExit(msg)
    url = settings.API_URL + f"ros/{identifier}/copyright/"
    data = {"ro": identifier,
            "agents": validated_agents}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def ros_add_funding(identifier, grant_identifier, grant_name, funder_name, grant_title=None, funder_doi=None):
    """
    Function that adds funding information to a specific research object.

    .. note::
        two auxiliary functions can be used to get some examples for funders and grants from the Zenodo database,
        respectively:
        :func:`~zenodo_list_funders`
        :func:`~zenodo_list_grants`
        check documentation of the above to get usage details

    :param identifier: research object's identifier
    :type identifier: str
    :param grant_identifier: grant's identifier
    :type grant_identifier: str
    :param grant_name: grant's name
    :type grant_name: str
    :param funder_name: funder's name
    :type funder_name: str
    :param grant_title: grant's title, optional
    :type grant_title: str
    :param funder_doi: funder's doi, optional
    :type funder_doi: str
    :returns: service identifier for the newly created funding
    :rtype: str
    """
    url = settings.API_URL + f"ros/{identifier}/fundings/"
    data = {"grant_identifier": grant_identifier,
            "grant_name": grant_name,
            "grant_title": grant_title,
            "funder_doi": funder_doi,
            "funder_name": funder_name}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content.get("identifier")


@validate_authentication_token
def ros_set_license(ros_id, license_id):
    """
    Function that sets license information associated with specific research object.

    .. seealso::
        :func:`~list_available_licenses`
        :func:`~list_custom_licenses`
        :func:`~add_custom_license`

    :param ros_id: research object's identifier
    :type ros_id: str
    :param license_id: license's identifier
    :type license_id: str
    :returns: response content from the API
    :rtype: dict
    """
    if not memo.licenses:
        memo.licenses = utils.get_available_licenses()
    if license_id not in memo.licenses:
        print("Incorrect license_id! You can check all available license options by running "
              " list_available_licenses().")
        return
    url = settings.API_URL + f"ros/{ros_id}/license/"
    data = {"identifier": license_id}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


###############################################################################
#              ROS upload methods.                                            #
###############################################################################


@validate_authentication_token
def ros_upload(path_to_zip):
    """
    Function that enables creating a new research object from the zip file.

    :param path_to_zip: path to the existing zip package
    :type path_to_zip: str
    :returns: response content from the API
    :rtype: dict
    """
    if os.path.isfile(path_to_zip):
        if zipfile.is_zipfile(path_to_zip):
            url = settings.API_URL + f"ros/upload/"
            r = utils.post_request_with_file(url=url, file=path_to_zip)
            content = r.json()
            job_id = content['identifier']
            if job_id:
                return is_job_success(job_id=job_id)
            else:
                msg = "Incorrect job response, couldn't validate if file was uploaded or not."
                raise SystemExit(msg)
        else:
            print("The file that was provided is not a real zip file! "
                  "Pleas try again with proper zip file.")
    else:
        print("Zip file doesn't exist! Please make sure passed path is correct!")


@validate_authentication_token
def ros_upload_resources(identifier, path_to_zip):
    """
    Function that enables creating a new resource from the zip file.

    :param identifier: research object's identifier
    :type identifier: str
    :param path_to_zip: path to the existing zip package
    :type path_to_zip: str
    :returns: response content from the API
    :rtype: dict
    """
    if os.path.isfile(path_to_zip):
        if zipfile.is_zipfile(path_to_zip):
            url = settings.API_URL + f"ros/{identifier}/resources/upload/"
            r = utils.post_request_with_file(url=url, file=path_to_zip)
            content = r.json()
            job_id = content['identifier']
            if job_id:
                return is_job_success(job_id=job_id)
            else:
                msg = "Incorrect job response, couldn't validate if file was uploaded or not."
                raise SystemExit(msg)
        else:
            print("The file that was provided is not a real zip file! "
                  "Pleas try again with proper zip file.")
    else:
        print("Zip file doesn't exist! Please make sure passed path is correct!")

###############################################################################
#              ROS delete methods.                                            #
###############################################################################


@validate_authentication_token
def ros_delete(identifier):
    """
    Function that deletes a specific research object.

    :param identifier: research object's identifier
    :type identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/"
    r = utils.delete_request(url=url)
    content = r.json()
    job_id = content['identifier']
    if job_id:
        return is_job_success(job_id=job_id)
    else:
        msg = "Incorrect job response, couldn't validate if file was uploaded or not."
        raise SystemExit(msg)


@validate_authentication_token
def ros_delete_funding(identifier, funding_identifier):
    """
    Function that deletes specific funding associated with specific research object.

    .. seealso::
        :func:`~ros_list_fundings`

    :param identifier: research object's identifier
    :type identifier: str
    :param funding_identifier: funding's identifier
    :type funding_identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/fundings/{funding_identifier}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("Funding successfully deleted!")
        return


@validate_authentication_token
def ros_delete_license(identifier):
    """
    Function that deletes association between license and specific research object.

    :param identifier: research object's identifier
    :type identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"ros/{identifier}/license/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("License successfully deleted!")
        return

###############################################################################
#              ROS put methods.                                               #
###############################################################################


@validate_authentication_token
def ros_update(identifier, title, research_areas, description=None, access_mode=None,
               ros_type=None, template=None, owner=None, editors=None,
               readers=None, creation_mode=None):
    """
    Function that updates specific research object.

    .. seealso::
        :func:`~list_valid_research_areas`
        :func:`~list_valid_access_modes`
        :func:`~list_valid_ros_types`
        :func:`~list_valid_templates`
        :func:`~list_valid_creation_modes`

    :param identifier: research object's identifier
    :type identifier: str
    :param title: title of your research object
    :type title: str
    :param research_areas: research areas associated with your research object
    :type research_areas: list
    :param description: description of your research object, optional
    :type description: str
    :param access_mode: research object's access mode, optional
    :type access_mode: str
    :param ros_type: research object's type, optional
    :type ros_type: str
    :param template: research object's template, optional
    :type template: str
    :param owner: research object's owner, optional
    :type owner: str
    :param editors: research object's editors, optional
    :type editors: list
    :param readers: research object's readers, optional
    :type readers: list
    :param creation_mode: research object's creation mode, optional
    :returns: response content from the API
    :rtype: dict
    """
    data = {"title": title,
            "research_areas": research_areas,
            "description": description,
            "access_mode": access_mode,
            "type": ros_type,
            "template": template,
            "owner": owner,
            "editors": editors,
            "readers": readers,
            "creation_mode": creation_mode}
    data = {key: value for key, value in data.items() if value is not None}
    url = settings.API_URL + f"ros/{identifier}/"
    r = utils.put_request(url=url, data=data, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def ros_update_funding(identifier, funding_identifier, grant_identifier=None, grant_name=None,
                       grant_title=None, funder_doi=None, funder_name=None):
    """
    Function that updates specific funding associated with specific research object.

    .. seealso::
        :func:`~ros_list_fundings`

    :param identifier: research object's identifier
    :type identifier: str
    :param funding_identifier: funding's identifier
    :type funding_identifier: str
    :param grant_identifier: grant's identifier, optional
    :type grant_identifier: str
    :param grant_name: grant's name, optional
    :type grant_name: str
    :param funder_name: funder's name, optional
    :type funder_name: str
    :param grant_title: grant's title, optional
    :type grant_title: str
    :param funder_doi: funder's doi, optional
    :type funder_doi: str
    :returns: response content from the API
    :rtype: dict
    """
    data = {"grant_identifier": grant_identifier,
            "grant_name": grant_name,
            "grant_title": grant_title,
            "funder_doi": funder_doi,
            "funder_name": funder_name}
    data = {key: value for key, value in data.items() if value is not None}
    url = settings.API_URL + f"ros/{identifier}/fundings/{funding_identifier}/"
    r = utils.patch_request(url=url, data=data)
    content = r.json()
    return content

###############################################################################
#              Resource main methods.                                         #
###############################################################################


@validate_authentication_token
def resource_search_using_id(identifier):
    """
    Function that displays details acquired from the API for the specific resource.

    :param identifier: resource's identifier
    :type identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"resources/{identifier}/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content


def resource_load(identifier):
    """
    Function that loads an existing resource.

    :param identifier: resource's identifier
    :type identifier: str
    :returns: loaded resource
    :rtype: Resource
    """
    return Resource.Resource(identifier=identifier, post_request=False)


@validate_authentication_token
def resource_assign_doi(identifier):
    """
    Function that assigns doi to a specific resource.

    :param identifier: resource's identifier
    :type identifier: str
    :returns: doi
    :rtype: str
    """
    url = settings.API_URL + f"resources/{identifier}/add_doi/"
    data = None
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content.get("doi")


@validate_authentication_token
def resource_download(identifier, resource_filename, path=None):
    """
    Function that acquires a specific resource into local file storage.

    :param identifier: resource's identifier
    :type identifier: str
    :param resource_filename: resource's full filename (with extension)
    :type resource_filename: str
    :param path: path where file should be downloaded, optional - current working dir is the default!
    :type path: str
    :returns: full path to the acquired resource
    :rtype: str
    """
    if path:
        os.makedirs(path, exist_ok=True)
        full_path = os.path.join(path, resource_filename)
    else:
        full_path = os.path.join(resource_filename)
    url = settings.API_URL + f"resources/{identifier}/download/"
    r = utils.get_request(url=url)
    content = r.content
    with open(full_path, 'wb') as out_file:
        out_file.write(content)
        if path:
            print(f"File was successfully downloaded into {path}.")
        else:
            print(f"File was successfully downloaded.")
        return full_path

###############################################################################
#              Resource delete methods.                                       #
###############################################################################


@validate_authentication_token
def resource_delete(identifier):
    """
    Function that deletes a resource associated with a specific research object.

    :param identifier: resource's identifier
    :type identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"resources/{identifier}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("Resource successfully deleted!")
        return

###############################################################################
#              Resource put methods.                                          #
###############################################################################


@validate_authentication_token
def resource_update_metadata(identifier, res_type=None, title=None,
                             folder=None, description=None):
    """
    Function that updates metadata for a specific resource.

    .. seealso::
        :func:`~list_valid_resource_types`

    :param identifier: resource's identifier
    :type identifier: str
    :param res_type: resource's type, optional
    :type res_type: str
    :param title: resource's title, optional
    :type title: str
    :param folder: folder's name, optional
    :type folder: str
    :param description: resource's description, optional
    :type description: str
    :returns: response content from the API
    :rtype: dict
    """
    if res_type:
        try:
            valid_resource_types = set(list_valid_resource_types())
            verified_res_type = utils.validate_against_different_formats(input_value=res_type,
                                                                         valid_value_set=valid_resource_types)
            # checking if set contains at least one element
            if len(verified_res_type):
                # expected behaviour, only one value is correct
                res_type = verified_res_type[0]
            else:
                msg = f"Incorrect resource type. Must be one of: {valid_resource_types}"
                raise SystemExit(msg)
        except KeyError:
            msg = "Something went wrong and we couldn't validate the resource type."
            print(msg)
    data = {"type": res_type,
            "title": title,
            "description": description,
            "folder": folder}
    data = {key: value for key, value in data.items() if value is not None}
    url = settings.API_URL + f"resources/{identifier}/"
    r = utils.patch_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def resource_update_content(identifier, input_url=None, file_path=None):
    """
    Function that updates content of specific resource.

    .. note::
        input_url is required for updating external resource, and file_path
        is in case of internal one. At least one of them has to be provided!

    .. warning::
        The resource content will be overwritten!

    :param identifier: resource's identifier
    :type identifier: str
    :param input_url: url to the external resource, optional
    :type input_url: str
    :param file_path: path to the internal resource, optional
    :type file_path: str
    :returns: response content from the API
    :rtype: dict
    """
    if not any([input_url, file_path]):
        msg = "One of arguments: input_url, file_path is required! File_path should be provided" \
              " for the internal resource, and input_url for the external."
        raise SystemExit(msg)
    if input_url and file_path:
        msg = "Incorrect usage: only one of input_url, file_path arguments should be provided!"
        raise SystemExit(msg)
    url = settings.API_URL + f"resources/{identifier}/"
    if file_path:
        if not os.path.isfile(file_path):
            msg = "ERROR: file_path doesn't point to an existing file!"
            raise SystemExit(msg)
        r = utils.patch_request_with_file_no_data(url=url, file=file_path)
    else:
        data = {"url": input_url}
        r = utils.patch_request(url=url, data=data)
    content = r.json()
    return content

###############################################################################
#              Folder methods.                                                #
###############################################################################


@validate_authentication_token
def folder_delete(folder_identifier):
    """
    Function that deletes a folder associated with specific research object.

    :param folder_identifier: folder's identifier
    :type folder_identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"folders/{folder_identifier}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("Folder successfully deleted!")
        return

###############################################################################
#              Annotation methods.                                            #
###############################################################################


@validate_authentication_token
def annotation_delete(annotation_identifier):
    """
    Function that deletes an annotation associated with specific research object.

    :param annotation_identifier: annotation's identifier
    :type annotation_identifier: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"annotations/{annotation_identifier}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("Resource successfully deleted!")
        return

###############################################################################
#              USER methods.                                                  #
###############################################################################


@validate_authentication_token
def users_find(search=None):
    """
    Function that finds a user against the provided query.

    .. warning::
        if no query provided then all users will be retrieved!

    :param search: query, optional
    :type search: str
    :returns: table containing selected information about users
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"search/users/"
    if search:
        params = {"search": search}
        r = utils.get_request_with_params(url=url, params=params)
    else:
        r = utils.get_request(url=url)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.loc[df["other"] == False]
        selected_columns = ['identifier', 'username', 'display_name', 'affiliation',
                            'description', 'areas_of_interest', 'orcid_identifier', 'external']
        df.drop(df.columns.difference(selected_columns), axis=1, inplace=True)
    return df


def show_user_id(username=None):
    """
    Function that displays user's identifier based on their username.

    :param username: username, optional - if not provided id for currently logged user will be retrieved
    :type username: str
    :returns: user's identifier
    :rtype: str
    """
    if not username:
        url = settings.API_URL + "users/whoami/"
        r = utils.get_request(url=url, use_token=True)
        content = r.json()
        try:
            user_id = content["identifier"]
        except KeyError as e:
            print("Ups... something went wrong. Couldn't read user's id from response.")
            print(e)
            return
    else:
        user_id = utils.search_for_user_id(username=username)
    return user_id


###############################################################################
#              EXTERNAL USER methods.                                         #
###############################################################################


@validate_authentication_token
def external_user_add(display_name, email=None, orcid_id=None, affiliation=None):
    """
    Function that creates an external user.

    .. note::
        Either email or orcid_id has to be provided in order to create new external user!

    :param display_name: displayed name for the user
    :type display_name: str
    :param email: user's email address, optional
    :type email: str
    :param orcid_id: user's orcid_id, optional
    :type orcid_id: str
    :param affiliation: user's affiliation, optional
    :type affiliation: str
    :returns: internal identifier for the newly created user
    :rtype: str
    """
    if not email and not orcid_id:
        msg = "Illegal usage: either email or orcid_id has to be provided in order to create user!"
        raise SystemExit(msg)
    url = settings.API_URL + f"external_users/"
    data = {"user_id": utils.generate_orcid_url(orcid_id) if orcid_id else email,
            "display_name": display_name,
            "email": email,
            "orcid_identifier": orcid_id,
            "affiliation": affiliation}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    identifier = content["identifier"]
    print(f"User successfully created with internal id: {identifier}!")
    return identifier


@validate_authentication_token
def external_user_delete(user_id):
    """
    Function that deletes an external user.

    :param user_id: str -> user's id
    :type user_id: str
    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"external_users/{user_id}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("External user successfully deleted!")
        return

###############################################################################
#              ORGANIZATIONS methods.                                         #
###############################################################################


@validate_authentication_token
def organization_add(display_name, email=None, organization_url=None,
                     ror_identifier=None):
    """
    Function that creates a new organization.

    .. note::
        Either email or ror_identifier has to be provided in order to create new organization!

    :param display_name: displayed name for the organization
    :type display_name: str
    :param email: organization's email address, optional
    :type email: str
    :param organization_url: organization's url, optional
    :type organization_url: str
    :param ror_identifier: organization's ror identifier, optional
    :type ror_identifier: str
    :returns: internal identifier for the newly created organization
    :rtype: str
    """
    if not email and not ror_identifier:
        msg = "Illegal usage: either email or ror_identifier has to be provided in order to create organization!"
        raise SystemExit(msg)
    url = settings.API_URL + f"organizations/"
    data = {"organization_id": utils.generate_ror_url(ror_identifier) if ror_identifier else email,
            "display_name": display_name,
            "email": email,
            "url": organization_url,
            "ror_identifier": ror_identifier}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    identifier = content["identifier"]
    print(f"Organization successfully created with internal id: {identifier}!")
    return identifier


@validate_authentication_token
def organizations_find(search=None):
    """
    Function that finds organization against the provided query.

    .. warning::
        if no query provided then all organizations will be retrieved!

    :param search: query, optional
    :type search: str
    :returns: table containing selected information about organizations
    :rtype: Panda's DataFrame
    """
    url = settings.API_URL + f"search/organizations/"
    if search:
        params = {"search": search}
        r = utils.get_request_with_params(url=url, params=params)
    else:
        r = utils.get_request(url=url)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    df = pd.DataFrame(results)
    return df

###############################################################################
#              Auxiliary methods.                                             #
###############################################################################


def zenodo_list_funders(number_of_results=settings.ZENODO_FUNDER_RESULTS_DEFAULT):
    """
    Function that displays list of funders from the Zenodo database.

    .. warning::
        number_of_results is limited to 100. The default value comes from
        settings file - ZENODO_FUNDER_RESULTS_DEFAULT!

    :param number_of_results: number of first "x" results that will be displayed, optional
    :type number_of_results: int
    :returns: selected information about funders
    :rtype: dict
    """
    if int(number_of_results) > 100:
        number_of_results = 100   # 100 is max!
    elif int(number_of_results) < 1:
        number_of_results = 1  # 1 is min !
    base_url = settings.ZENODO_FUNDERS_URL
    url = base_url + f"?sort=bestmatch&page=1&size={number_of_results}"
    r = utils.get_request(url=url, use_token=False)
    content = r.json()
    results = {}
    counter = 1
    while counter <= number_of_results:
        for hit in content["hits"]["hits"]:
            api_url = hit.get("links").get("self")
            acronym = hit.get("metadata").get("acronyms")
            identifiers = hit.get("metadata").get("identifiers")
            name = hit.get("metadata").get("name")
            doi = hit.get("metadata").get("doi")
            results.update({counter: {"api_url": api_url,
                                      "acronym": acronym,
                                      "identifiers": identifiers,
                                      "name": name,
                                      "doi": doi
                                      }})
            counter += 1
    return results


def zenodo_list_grants(number_of_results=settings.ZENODO_GRANT_RESULTS_DEFAULT):
    """
    Function that displays list of grants from the Zenodo database.

    .. warning::
        number_of_results is limited to 100. The default value comes from
        settings file - ZENODO_GRANT_RESULTS_DEFAULT!

    :param number_of_results: number of first "x" results that will be displayed, optional
    :type number_of_results: int
    :returns: selected information about grants
    :rtype: dict
    """
    if int(number_of_results) > 100:
        number_of_results = 100   # 100 is max!
    elif int(number_of_results) < 1:
        number_of_results = 1  # 1 is min !
    base_url = settings.ZENODO_GRANTS_URL
    url = base_url + f"?sort=bestmatch&page=1&size={number_of_results}"
    r = utils.get_request(url=url, use_token=False)
    content = r.json()
    results = {}
    counter = 1
    while counter <= number_of_results:
        for hit in content["hits"]["hits"]:
            api_url = hit.get("links").get("self")
            acronym = hit.get("metadata").get("acronym")
            identifiers = hit.get("metadata").get("identifiers")
            title = hit.get("metadata").get("title")
            funder = hit.get("metadata").get("funder").get("name")
            results.update({counter: {"api_url": api_url,
                                      "acronym": acronym,
                                      "identifiers": identifiers,
                                      "title": title,
                                      "funder": funder
                                      }})
            counter += 1
    return results


def list_available_licenses():
    """
    Function that lists all available options for the license identifier.

    :returns: all available license identifiers
    :rtype: list
    """
    if not memo.licenses:
        memo.licenses = utils.get_available_licenses()
    return memo.licenses


def list_valid_research_areas():
    """
    Function that lists all valid research areas.

    :returns: valid research areas
    :rtype: list
    """
    if not memo.research_areas:
        r = utils.get_request(url=settings.API_URL + "research-areas/")
        if r:
            content = r.json()
            results = content.get("results")
            while content["next"]:
                r = utils.get_request(url=content["next"])
                content = r.json()
                results.extend(content.get("results"))
            for result in results:
                memo.research_areas.append(result['name'])
        else:
            msg = "Something went wrong... Couldn't access valid research areas. Please try again."
            print(msg)
            return
    return memo.research_areas


def list_valid_access_modes():
    """
    Function for listing all valid access modes.

    :returns: valid access modes
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["ro_access_mode"]


def list_valid_ros_types():
    """
    Function that lists all valid ros types.

    :returns: valid ros types
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["ro_type"]


def list_valid_templates():
    """
    Function that lists all valid templates.

    :returns: valid templates
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["ro_template"]


def list_valid_creation_modes():
    """
    Function that lists all valid creation modes.

    :returns: valid creation modes
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["ro_creation_mode"]


def list_valid_resource_types():
    """
    Function for lists all valid resource types.

    :returns: valid resource types
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["resource_type"]


def list_valid_publication_services():
    """
    Function that lists all valid publication services.

    :returns: valid publication services
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["publication_service"]


def list_valid_license_status():
    """
    Function that lists all valid statuses for the custom license.

    :returns: valid license statuses
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["license_status"]


def list_triple_object_classes():
    """
    Function that lists all valid triple object classes.

    :returns: valid triple object classes
    :rtype: list
    """
    if not memo.service_enums:
        memo.service_enums = utils.get_available_enums()
    return memo.service_enums["triple_object_class"]


@validate_authentication_token
def list_custom_licenses():
    """
    Function that lists existing custom licenses.

    :returns: existing custom licenses
    :rtype: list
    """
    url = settings.API_URL + f"custom-licenses/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    results = content.get("results")
    while content["next"]:
        r = utils.get_request(url=content["next"])
        content = r.json()
        results.extend(content.get("results"))
    if results:
        return results
    else:
        msg = "Unexpected error. Couldn't obtain custom licenses results."
        print(msg)


@validate_authentication_token
def add_custom_license(identifier, title, status, license_url, description=None):
    """
    Function that adds a new custom license.

    .. seealso::
        :func:`~list_valid_license_status`

    :param identifier: license's identifier
    :type identifier: str
    :param title: license's title
    :type title: str
    :param status: license's status
    :type status: str
    :param license_url: license's url
    :type license_url: str
    :param description: license's description, optional
    :type description: str
    :returns: response content from the API
    :rtype: dict
    """
    try:
        valid_status = set(list_valid_license_status())
        verified_status = utils.validate_against_different_formats(input_value=status,
                                                                   valid_value_set=valid_status)
        # checking if set contains at least one element
        if len(verified_status):
            # expected behaviour, only one value is correct
            status = verified_status[0]
        else:
            msg = f"Incorrect resource type. Must be one of: {valid_status}"
            raise SystemExit(msg)
    except Exception as e:
        msg = "Unexpected error: couldn't validate license status value."
        print(msg)
        print(e)

    url = settings.API_URL + f"custom-licenses/"
    data = {"identifier": identifier,
            "title": title,
            "status": status,
            "url": license_url,
            "description": description}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.post_request(url=url, data=data)
    content = r.json()
    return content


@validate_authentication_token
def update_custom_license(identifier, title, status, license_url, description=None):
    """
    Function that updates a custom license.

    .. seealso::
        :func:`~list_valid_license_status`

    :param identifier: license's identifier
    :type identifier: str
    :param title: license's title
    :type title: str
    :param status: license's status
    :type status: str
    :param license_url: license's url
    :type license_url: str
    :param description: license's description, optional
    :type description: str
    :returns: response content from the API
    :rtype: dict
    """
    try:
        valid_status = set(list_valid_license_status())
        verified_status = utils.validate_against_different_formats(input_value=status,
                                                                   valid_value_set=valid_status)
        # checking if set contains at least one element
        if len(verified_status):
            # expected behaviour, only one value is correct
            status = verified_status[0]
        else:
            msg = f"Incorrect resource type. Must be one of: {valid_status}"
            raise SystemExit(msg)
    except Exception as e:
        msg = "Unexpected error: couldn't validate license status value."
        print(msg)
        print(e)

    url = settings.API_URL + f"custom-licenses/{identifier}/"
    data = {"identifier": identifier,
            "title": title,
            "status": status,
            "url": license_url,
            "description": description}
    data = {key: value for key, value in data.items() if value is not None}
    r = utils.put_request(url=url, data=data, use_token=True)
    content = r.json()
    return content


@validate_authentication_token
def show_valid_type_matching_for_ros():
    """
    Function that displays valid pairs for ros_type and template.

    :returns: response content from the API
    :rtype: dict
    """
    url = settings.API_URL + f"ros/type_matching/"
    r = utils.get_request(url=url, use_token=True)
    content = r.json()
    return content
