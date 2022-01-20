"""Create a Bitbucket Pull Request. (Not Implemented)"""
import os
import datetime
import requests

def main(args):
    raise NotImplementedError("This is only half implemented")


def build_pull_request_json(project, repo_slug, from_branch, to_branch, title, description):
    return {
        "title": title,
        "description": description,
        "state": "OPEN",
        "open": True,
        "closed": False,
        "fromRef": {
            "id": f"refs/heads/{from_branch}",
            "repository": {
                "slug": repo_slug,
                "project": {
                    "key": project,
                }
            }
        },
        "toRef": {
            "id": f"refs/heads/{to_branch}",
            "repository": {
                "slug": repo_slug,
                "project": {
                    "key": project
                }
            }
        },
        "locked": False
    }
    # END build_pull_request_json

def _post_pull_request(args):
    # Parameters from environment variables (should be populated by the Jenkinsfile)
    try:
        from_branch_name = os.environ['FROM_BRANCH']
        to_branch_name = os.environ['TO_BRANCH']
        git_uo_user = os.environ['USER']
        git_uo_password = os.environ['PASSWORD']
        project = os.environ['PROJECT']
        repo_slug = os.environ['REPO']
    except KeyError as internal_error:
        raise ValueError('Missing required environment variable(s), see internal exception. '
                         'NOTE: more environment variables may be missing, please consult the source code.') \
            from internal_error

    # Create the pull request JSON object to be POSTed
    pull_request_json = build_pull_request_json(
        project,
        repo_slug,
        from_branch_name,
        to_branch_name,
        title=f"""[AUTO] pip updates, {datetime.now().strftime("%d %B, %Y")}""",
        description="Automatically generated pull request to check for updates."
    )

    # Make the request
    try:
        response = requests.post(
            f'{args.bitbucket_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/pull-requests',
            json=pull_request_json, auth=(git_uo_user, git_uo_password))
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"[ERROR] HTTP Error ({error.response.status_code}): {error.response.text}")
        exit(-1)
