from typing import Callable, List

import casbin
import falcon


class CasbinMiddleware:
    """
    A middleware for Casbin.

    :param str model: Path to model file
    :param str policy: Path to policy file
    :param casbin.Adapter adapter: Adapter object instance
    :param str default_role: Default role to use if no roles are found
    :param str roles_header: Header to check for roles
    :param forbidden_message: Message to return on failed authorization
    :param success_callback: Function to run on successful authorization
    :param failure_callback: Function to run on failed authorization
    """

    def __init__(
        self,
        model: str,
        policy: str = None,
        adapter: casbin.Adapter = None,
        default_role: str = "any",
        enable_roles_header: bool = False,
        roles_header: str = "X-Roles",
        forbidden_message: str = None,
        success_callback: Callable[[str, str, str], None] = None,
        failure_callback: Callable[[List[str], str, str], None] = None,
    ):
        self.model = model
        self.policy = policy
        self.adapter = adapter
        self.default_role = default_role
        self.enable_roles_header = enable_roles_header
        self.roles_header = roles_header
        self.forbidden_message = (
            forbidden_message or "Access to this resource has been restricted"
        )
        self.success_callback = success_callback
        self.failure_callback = failure_callback

        if not self.policy and not self.adapter:
            raise ValueError("Must specify a policy or an adapter")

    def process_resource(self, req, resp, resource, params):
        if self.policy:
            e = casbin.Enforcer(self.model, self.policy)
        else:
            e = casbin.Enforcer(self.model, self.adapter)

        roles = getattr(req.context, "roles", None)

        if not roles and self.enable_roles_header:
            roles_header = req.get_header(self.roles_header, default=self.default_role)
            roles = [role.strip() for role in roles_header.split(",")]

        roles = roles or [self.default_role]

        obj = req.uri_template
        act = req.method.upper()

        authorized = False
        for role in roles:
            if e.enforce(role, obj, act):
                authorized = True
                if self.success_callback:
                    self.success_callback(role, obj, act)
                break

        if not authorized:
            if self.failure_callback:
                self.failure_callback(roles, obj, act)
            raise falcon.HTTPForbidden(description=self.forbidden_message)
