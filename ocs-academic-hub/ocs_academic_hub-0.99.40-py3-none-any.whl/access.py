from IPython.display import display, Javascript
import requests
import json
import os

HUB_BASE_URL = "https://data.academic.osisoft.com"
AUTH_ENDPOINT = f"{HUB_BASE_URL}/auth"


def jss(session_id):
    return f"""
    let t = JSON.stringify(localStorage.getItem("hub_jwt") || '{{"access_token": "none"}}', null, 4);
    const options = {{
        method: 'POST',
        body: JSON.stringify(t),
        headers: {{
            'Content-Type': 'application/json',
            'Authorization': 'Custom {session_id}'
        }},
        // mode: 'no-cors'
    }}; 
    fetch('{AUTH_ENDPOINT}/previous_token', options) 
    .then(function (response) {{
        return response.text();
    }})
    .catch(function (error) {{
        console.log("Error: " + error);
    }});
    """


def js(session_id):
    return Javascript(jss(session_id))


def restore_previous_jwt(session_id):
    display(js(session_id))


def save_jwt(jwt):
    tjss = f"""
        let t1 = JSON.stringify(JSON.parse('{json.dumps(jwt)}'));
        localStorage.setItem("hub_jwt", t1);
    """
    display(Javascript(tjss))


def delete_jwt():
    tjs = f"""
        localStorage.removeItem("hub_jwt");
    """
    display(Javascript(tjs))


def client_jwt():
    cid, csec = os.environ.get("HUB_CREDS").split(":")
    r = requests.post(
        "https://dev-f0ejox1i.auth0.com/oauth/token",
        headers={"content-type": "application/json"},
        json={
            "client_id": cid,
            "client_secret": csec,
            "audience": "https://data.academic.osisoft.com",
            "grant_type": "client_credentials",
        },
    )
    jwt = {"access_token": "none"}
    if 200 == r.status_code:
        jwt = r.json()
        jwt["id_token"] = jwt.pop("access_token")
        jwt["creds"] = 1

    return jwt


def get_previous_jwt(session_id):
    if os.environ.get("HUB_CREDS", None):
        return client_jwt()
    r = requests.get(
        f"{AUTH_ENDPOINT}/previous_token",
        headers={"Authorization": f"Custom {session_id}"},
        verify=False,
    )
    if 200 == r.status_code:
        return eval(json.loads(r.text))
    else:
        return {"access_token": "none"}
