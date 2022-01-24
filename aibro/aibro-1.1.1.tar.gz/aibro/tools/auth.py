from getpass import getpass
from typing import Optional
from typing import Tuple

from aibro.constant import IS_DEMO
from aibro.tools.prints import print_err
from aibro.tools.service.api_service import aibro_client
from aibro.tools.utils import sha256_encode

AUTHENTICATED_USER_ID = None


def check_authentication(access_token: str = None) -> Optional[Tuple[str, str]]:
    global AUTHENTICATED_USER_ID
    if not AUTHENTICATED_USER_ID:
        if IS_DEMO:
            email = input("Welcome! To launch a trial, please enter your email: ")
            data = {"email": email, "password": "demo"}
        elif access_token:
            data = {"access_token": access_token}
        else:
            email = input("Enter your email: ")
            password = getpass()
            encoded = sha256_encode(password)
            data = {"email": email, "password": encoded}
        try:
            resp = aibro_client.post_with_json_data(
                "v1/authenticate", data, handle_error=False
            )
            if resp.status_code == 402:
                AUTHENTICATED_USER_ID = resp.json()["user_id"]
                while True:
                    username = input("Create a username: ")
                    data = {
                        "user_id": AUTHENTICATED_USER_ID,
                        "username": username,
                    }
                    resp_2 = aibro_client.post_with_json_data(
                        "v1/create_username", data, handle_error=False
                    )
                    if resp_2.status_code != 200:
                        print(resp_2.text)
                        continue
                    print(resp_2.text)
                    break
            AUTHENTICATED_USER_ID = resp.json()["user_id"]
        except Exception as e:
            print_err(f"Authentication Error: {str(e)}")
            return None
    else:
        if IS_DEMO:
            print("Already entered email!")
        else:
            print("Already authenticated!")

    return AUTHENTICATED_USER_ID
