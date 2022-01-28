import requests
import pandas as pd
import xmltodict


class OdkError(Exception):
    pass


def get_odk_data(aggregate_url: str, username: str, password: str, form_id: str) -> pd.DataFrame:
    submissions = get_odk_submissions(aggregate_url, form_id, password, username)
    return pd.DataFrame(submissions)


def get_odk_submissions(aggregate_url, form_id, password, username, form_group=''):
    auth = requests.auth.HTTPDigestAuth(username, password)
    submissions = requests.get(aggregate_url + "/view/submissionList",
                               params={"formId": form_id}, auth=auth)
    if submissions.status_code >= 400:
        raise OdkError(f"Failed to get submissions for form {form_id}")
    try:
        submissions_dict = xmltodict.parse(submissions.text)["idChunk"]
    except xmltodict.ParsingInterrupted:
        raise ValueError("Can not parse xml")
    _response_id_list = submissions_dict["idList"]
    if not _response_id_list:
        return []
    submissions_ids = _response_id_list["id"]
    if not isinstance(submissions_ids, list):
        submissions_ids = [submissions_ids]
    for submission_id in submissions_ids:
        yield __get_odk_submission(aggregate_url, auth, form_id, submission_id, form_group)


def __get_odk_submission(aggregate_url: str, auth: requests.auth.HTTPDigestAuth,
                         form_id: str, uuid: str, form_group: str = '') -> dict:
    if not form_group:
        form_group = form_id
    form_id_string = f'{form_id}[@version=null and @uiVersion=null]/{form_group}[@key={uuid}]'
    submission = requests.get(aggregate_url + "/view/downloadSubmission",
                              params={"formId": form_id_string}, auth=auth)
    if submission.status_code >= 400:
        raise OdkError(f"Failed to get submissions for form {form_id}")
    submission = xmltodict.parse(submission.text)["submission"]["data"][f"{form_group}"]
    return __fix_odk_data(submission)


def __fix_odk_data(form_submission: dict) -> dict:
    return_submission = {}
    for key, value in form_submission.items():
        if key not in ["orx:meta"]:
            new_key = key.replace("@", "")
            return_submission[new_key] = value
    return return_submission
