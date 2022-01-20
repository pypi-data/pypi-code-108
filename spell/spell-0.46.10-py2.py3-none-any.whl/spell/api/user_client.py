from spell.api import base_client
from spell.api.utils import url_path_join


USER_RESOURCE_URL = "users"


class UserClient(base_client.BaseClient):
    def create(
        self,
        user_name,
        email,
        password,
        recaptcha_token,
        full_name=None,
        organization=None,
        terms_accepted=False,
    ):
        """Create a new user at the server

        Keyword arguments:
        user_name -- user_name of the new user (must be at least 4 characters)
        email -- email of the new user
        password -- password of the new user (must be at least 8 characters)
        full_name -- full name of new user
        organization -- optional, company or group new user is associated with

        Returns:
        a User object for the new user

        """
        payload = {
            "user": {
                "user_name": user_name,
                "password": password,
                "email": email,
                "full_name": full_name,
                "organization": organization,
                "terms_accepted": terms_accepted,
            },
            "recaptcha_token": recaptcha_token,
        }
        r = self.request("post", USER_RESOURCE_URL, payload=payload, requires_login=False)
        self.check_and_raise(r)

        # Workaround tests that do not take cookies into account
        # TODO(jay): Fix the tests!
        self.session.cookies.clear()

        return self.get_json(r)["user"]

    def _login(self, user_name, email, password, access_token):
        """Log in a user to the server

        Keyword arguments:
        user_name -- user_name of the user
        email -- email of the user
        password -- password of the user
        access_token -- an access token for the user

        Returns:
        a User object and an authentication token for the user

        """
        payload = {"user": {"user_name": user_name, "password": password, "email": email, "access_token": access_token}}
        r = self.request(
            "post",
            "{}/{}".format(USER_RESOURCE_URL, "login"),
            payload=payload,
            requires_login=False,
        )
        self.check_and_raise(r)
        resp = self.get_json(r)
        self.token = resp["token"]
        self.spell_admin_token = resp.get("spell_admin_token", None)
        return resp["user"], self.token, self.spell_admin_token

    def login_with_email(self, email, password):
        """Log in a user by email to the server

        Keyword arguments:
        email -- email of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        return self._login("", email, password, "")

    def login_with_username(self, user_name, password):
        """Log in a user by user_name to the server

        Keyword arguments:
        user_name -- user_name of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        return self._login(user_name, "", password, "")

    def login_with_access_token(self, email, access_token):
        """Log in a user by access token to the server

        Keyword arguments:
        email -- a valid user email
        access_token -- a valid user access token

        Returns:
        an authentication token for the user
        """
        return self._login("", email, "", access_token)

    def logout(self):
        """Log out a user from the server"""
        r = self.request("post", "{}/{}".format(USER_RESOURCE_URL, "logout"))
        self.check_and_raise(r)

    def check_password(self, password):
        """Checks password for a logged-in user

        Keyword arguments:
        password -- password of the user

        Returns:
        nothing if successful
        """
        payload = {"password": password}
        r = self.request("post", "{}/{}".format(USER_RESOURCE_URL, "me/check_password"), payload=payload)
        self.check_and_raise(r)

    def change_password(self, old_password, new_password):
        """Change password for a logged-in user, require password before changing

        Keyword arguments:
        old_password -- current password for the user
        new_password -- new password for the user

        Returns:
        nothing if successful

        """
        payload = {
            "new_password": new_password,
            "old_password": old_password,
        }
        r = self.request("put", "{}/{}".format(USER_RESOURCE_URL, "me/change_password"), payload=payload)
        self.check_and_raise(r)

    def get_user_info(self):
        """Get user information from the server

        Returns:
        a User object for the user

        """
        r = self.request("get", "{}/{}".format(USER_RESOURCE_URL, "me"))
        self.check_and_raise(r)
        return self.get_json(r)["user"]

    def get_billing_info(self):
        """Get user billing information from the server

        Returns:
        a Billing object for the user

        """
        r = self.request("get", url_path_join("billing", self.owner, "status"))
        self.check_and_raise(r)
        return self.get_json(r)["billing_status"]

    def list_access_tokens(self):
        """List all user access tokens

        Returns:
        a list of access token objects

        """
        r = self.request("get", url_path_join(USER_RESOURCE_URL, "me", "access_tokens"))
        self.check_and_raise(r)
        return self.get_json(r)["access_tokens"]

    def create_access_token(self, name):
        """Create a new access token with the given name

        Returns:
        a single access token object including the Token

        """
        r = self.request(
            "post",
            url_path_join(USER_RESOURCE_URL, "me", "access_tokens"),
            payload={"name": name},
        )
        self.check_and_raise(r)
        return self.get_json(r)

    def delete_access_token(self, name):
        """Deletes an existing access token with the given name

        Returns:
        nothing if successful

        """
        r = self.request(
            "delete",
            url_path_join(USER_RESOURCE_URL, "me", "access_tokens"),
            payload={"name": name},
        )
        self.check_and_raise(r)
