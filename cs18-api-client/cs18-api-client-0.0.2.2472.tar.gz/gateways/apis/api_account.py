from gateways.apis.api_base_class import ApiBase
from gateways.common.cs18_api_requests import NewUserSurveyRequest


class ApiAccount(ApiBase):
    def account_register(self):
        return self.build_route("accounts/register")

    def contact_me(self):
        return self.build_route("accounts/contactme")

    def account_login(self, account: str):
        return self.build_route(f"accounts/{account}/login")

    def get_account_extra_details(self, account: str):
        return self.build_route(f"accounts/{account}/details")

    def forgot_password(self):
        return self.build_route("accounts/forgotpassword")

    def reset_password(self):
        return self.build_route("accounts/resetpassword")

    def invitations(self):
        return self.build_route("accounts/invitations")

    def account_signup_by_secret(self, secret: str):
        return self.build_route(f"accounts/signup/{secret}")

    def account_signup(self):
        return self.build_route("accounts/signup")

    def account_invitations(self, space: str = None):
        return self.build_route(
            "accounts/invitations" + (f"?space_name={space}" if space else "")
        )

    def account_users(self):
        return self.build_route("accounts/users")

    def account_user(self, user_email: str):
        return self.build_route(f"accounts/users/{user_email}")

    def account_user_account_role_value(self, user_email: str, account_role: str):
        return self.build_route(
            f"accounts/users/{user_email}/account_role?value={account_role}"
        )

    def account_user_account_role(self, user_email: str):
        return self.build_route(f"accounts/users/{user_email}/account_role")

    def delete_account(self, account_name: str) -> str:
        return self.build_route(f"accounts/{account_name}")

    def set_account_extra_details(self, account_name: str) -> str:
        return self.build_route(f"accounts/{account_name}/details")

    def submit_new_user_survey(self) -> str:
        return self.build_route(f"accounts/roles_and_technologies")
