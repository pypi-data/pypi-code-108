from gateways.apis.api_base_class import ApiBase


class ApiSpaces(ApiBase):
    def spaces(self):
        return self.build_route("spaces")

    def space_by_name(self, space_name: str):
        return self.build_route("spaces/{space_name}".format(**locals()))

    def get_images(self, space_name: str, cloud_account_name: str, region_id: str):
        return self.build_route("spaces/{space_name}/cloud_accounts/AWS/{cloud_account_name}/regions/{"
                                "region_id}/private_images"
                                .format(**locals()))

    def get_instance_types(self, space_name: str, cloud_account_name: str, region_id: str):
        return self.build_route("spaces/{space_name}/cloud_accounts/AWS/{cloud_account_name}/regions/{"
                                "region_id}/instance_types"
                                .format(**locals()))

    def space_users(self, space_name: str):
        """Astronauts"""
        return self.build_route("spaces/{space_name}/users".format(**locals()))

    def space_repositories(self, space_name: str, repository_type: str = None, deployment_type: str = None):
        if repository_type is None:

            if deployment_type is None:
                return self.build_route("spaces/{space_name}/repositories".format(**locals()))
            return self.build_route("spaces/{space_name}/repositories?type={deployment_type}".format(**locals()))

        if repository_type == 'bitbucket':
            return self.space_bitbucket_repositories(space_name)

        return self.space_github_repositories(space_name)

    def space_cloud_accounts(self, space_name: str):
        return self.build_route("spaces/{space_name}/cloud_accounts".format(**locals()))

    def space_cloud_account(self, space_name: str, cloud_account: str):
        return self.build_route(
            "spaces/{space_name}/cloud_accounts/{cloud_account}".format(**locals())
        )

    def space_cloud_account_compute_services(self, space_name: str, cloud_account: str):
        return self.build_route(
            "spaces/{space_name}/cloud_accounts/{cloud_account}/compute_services".format(**locals())
        )

    def space_cloud_account_compute_service(self, space_name: str, cloud_account: str, compute_service: str):
        return self.build_route(
            "spaces/{space_name}/cloud_accounts/{cloud_account}/compute_services/{compute_service}".format(**locals())
        )

    def space_github_repositories(self, space_name: str):
        return self.build_route(
            "spaces/{space_name}/repositories/github".format(**locals())
        )

    def space_bitbucket_repositories(self, space_name: str):
        return self.build_route(
            "spaces/{space_name}/repositories/bitbucket".format(**locals())
        )

    def user_permissions(self, space_name: str):
        return self.build_route("spaces/{space_name}/user_permissions".format(**locals()))

    def space_user(self, space_name: str, user_email: str):
        return self.build_route("spaces/{space_name}/users/{user_email}".format(**locals()))

    def user_space_role(self, space_name: str, user_email: str, space_role_name: str):
        return self.build_route(
            "spaces/{space_name}/users/{user_email}/space_role?value={space_role_name}".format(**locals())
        )

    def space_cloud_account_regions(self, space_name: str, cloud_account_name: str):
        return self.build_route(
            "spaces/{space_name}/cloud_accounts/{cloud_account_name}/regions".format(**locals())
        )

    def space_sandbox_repository(self, space_name):
        return self.build_route(
            "spaces/{space_name}/sandbox_repository".format(**locals())
        )

    def space_production_repository(self, space_name):
        return self.build_route(
            "spaces/{space_name}/production_repository".format(**locals())
        )

    def add_repository_relationship(self, space_name: str):
        return self.build_route(f"spaces/{space_name}/repository_relationships")

    def repository_relationship(self, space_name: str, deployment_type: str):
        return self.build_route(f"spaces/{space_name}/repository_relationships/{deployment_type}")

    def custom_space_tags(self, space_name: str):
        return self.build_route(f"spaces/{space_name}/settings/tags")

    def custom_space_tag(self, space_name: str, name: str):
        return self.build_route(f"spaces/{space_name}/settings/tags/{name}")

    def custom_blueprint_tags(self, space_name: str, blueprint_name: str, deployment_type: str):
        return self.build_route(f"spaces/{space_name}/blueprints/{blueprint_name}/settings/tags?type={deployment_type}")

    def custom_blueprint_tag(self, space_name: str, blueprint_name: str, name: str, deployment_type: str):
        return self.build_route(f"spaces/{space_name}/blueprints/{blueprint_name}/settings/tags/{name}?type={deployment_type}")

    def available_space_terraform_modules(self, space_name: str) -> str:
        return self.build_route(f"spaces/{space_name}/tfmodules/available")

    def attached_space_terraform_modules(self, space_name: str) -> str:
        return self.build_route(f"spaces/{space_name}/tfmodules/attached")

    def attached_space_terraform_module(self, space_name: str, module_alias: str) -> str:
        return self.build_route(f"spaces/{space_name}/tfmodules/attached/{module_alias}")
      