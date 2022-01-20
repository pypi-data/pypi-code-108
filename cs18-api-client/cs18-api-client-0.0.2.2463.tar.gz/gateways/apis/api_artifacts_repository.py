from gateways.apis.api_base_class import ApiBase


class ApiArtifactsRepository(ApiBase):
    def azure_storage(self, space_name: str):
        return self.build_route(f"spaces/{space_name}/artifactrepos/azurestorage")

    def aws_s3_storage(self, space_name: str):
        return self.build_route(f"spaces/{space_name}/artifactrepos/awss3")

    def artifact_repos(self, space_name: str):
        return self.build_route(f"spaces/{space_name}/artifactrepos")

    def artifact_repos_by_cloud_account_name(
        self, cloud_account_name: str, space_name: str
    ):
        return self.build_route(
            f"spaces/{space_name}/artifactrepos/{cloud_account_name}/storage"
        )

    def artifactory(self, space_name: str):
        return self.build_route(f"spaces/{space_name}/artifactrepos/artifactory")
