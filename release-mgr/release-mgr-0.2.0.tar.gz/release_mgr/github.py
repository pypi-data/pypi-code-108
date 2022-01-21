import requests


def create_release(
    token,
    repo,
    tag_name,
    name,
    body,
    draft=False,
    prerelease=False,
):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    body = {
        "tag_name": tag_name,
        "name": name,
        "body": body,
        "draft": draft,
        "prerelease": prerelease,
    }

    response = requests.post(
        f"https://api.github.com/repos/{repo}/releases",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
