from gateways.apis.api_base_class import ApiBase


class ApiDebugging(ApiBase):
    def get_aws_pem_file(self, space_name: str, sandbox_id: str, instance_id: str):
        return self.build_route(
            "spaces/{space_name}/direct_connect/ssh/aws/{sandbox_id}/{instance_id}/pem_file".format(**locals()))

    def get_direct_aws_ssh_connect(self, space_name: str, sandbox_id: str, instance_id: str):
        return self.build_route(
            "spaces/{space_name}/direct_connect/ssh/aws/{sandbox_id}/{instance_id}/".format(**locals()))

    def get_direct_azure_ssh_connect(self, space_name: str, sandbox_id: str, instance_id: str):
        return self.build_route(
            "spaces/{space_name}/direct_connect/ssh/azure/{sandbox_id}/{instance_id}/".format(**locals()))

    def get_direct_rpd_file(self, space_name: str, sandbox_id: str, instance_id: str):
        return self.build_route(
            "spaces/{space_name}/direct_connect/rdp/{sandbox_id}/{instance_id}/rdp_file".format(**locals()))

    def get_direct_rpd_connect(self, space_name: str, sandbox_id: str, instance_id: str):
        return self.build_route(
            "spaces/{space_name}/direct_connect/rdp/{sandbox_id}/{instance_id}/".format(**locals()))
