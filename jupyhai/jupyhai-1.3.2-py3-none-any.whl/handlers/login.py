from valohai_cli.api import request
from valohai_cli.exceptions import APIError, APINotFoundError, CLIException

from jupyhai.api_urls import ME_URL, SERVER_INFO_URL
from jupyhai.consts import HOST, NOTEBOOK_INSTANCE_ID
from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils.auth import (
    get_current_username,
    login_status,
    login_with_credentials,
    verify_and_save_token,
)


class LoginHandler(JupyhaiHandler):
    def get(self) -> None:
        flavor = None
        logged_in = login_status()
        if logged_in:
            try:
                request('GET', ME_URL).json()
            except APIError as ae:
                # TODO: this is a terrible hack :(
                if 'token_expired' in str(ae):
                    logged_in = False

            try:
                response = request('GET', SERVER_INFO_URL)
                flavor = response.json()['flavor']
            except APINotFoundError:
                flavor = "valohai"

        username = get_current_username()
        self.finish(
            {
                "logged_in": logged_in,
                "username": username,
                "notebook_instance_id": NOTEBOOK_INSTANCE_ID,
                "host_flavor": flavor,
                "default_host": HOST,
            }
        )

    def post(self) -> None:
        args = self.get_json_body()
        try:
            host = args['hostUrl']
            if not host.startswith('http://') and not host.startswith('https://'):
                host = 'http://' + host

            if args.get('token'):
                self.log.info(f"Logging in with token into {host}...")
                verify_and_save_token(args['token'], host)
            else:
                self.log.info(f"Logging in with username + password into {host}...")
                login_with_credentials(
                    username=args['username'],
                    password=args['password'],
                    host=host,
                )
        except APIError as e:
            try:
                error_json = e.response.json()
                if isinstance(error_json, dict) and 'message' in error_json:
                    self.finish({'success': False, 'error': error_json['message']})
                    return
                else:
                    raise ValueError
            except Exception:
                self.finish({'success': False, 'error': e.message})
                return
        except CLIException as e:
            self.finish({'success': False, 'error': e.message})
            return
        except Exception as e:
            self.finish({'success': False, 'error': str(e)})
            return

        self.finish({'success': login_status()})
