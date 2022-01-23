from gateways.apis.api_base_class import ApiBase


class ApiSandbox(ApiBase):
    def __init__(self, api_address: str, space_name: str, version: str = None):
        super().__init__(api_address, version)
        self._space = space_name

    def sandboxes(self):
        return self.build_route("spaces/{self._space}/sandbox".format(**locals()))


    def sandbox_by_id(self, sandbox_id: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}".format(**locals())
        )

    def sandbox_app_logs(self, sandbox_id: str, app_name: str, infra_id: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/{app_name}/{infra_id}".format(
                **locals()
            )
        )

    def sandbox_tfstate(self, sandbox_id: str, service_name: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/tfstate?service_name={service_name}".format(**locals())
        )

    def sandbox_preparetags(self, sandbox_id: str, service_name: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/preparetags?service_name={service_name}".format(**locals())
        )

    def sandbox_tfinit(self, sandbox_id: str, service_name: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/tfinit?service_name={service_name}".format(**locals())
        )

    def sandbox_tfplan(self, sandbox_id: str, service_name: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/tfplan?service_name={service_name}".format(**locals())
        )

    def sandbox_tfapply(self, sandbox_id: str, service_name: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/tfapply?service_name={service_name}".format(**locals())
        )

    def sandbox_tfdestroy(self, sandbox_id: str, service_name: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/logs/tfdestroy?service_name={service_name}".format(**locals())
        )

    def sandbox_scheduled_end_time(self, sandbox_id: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/scheduled_end_time".format(
                **locals()
            )
        )

    def sandbox_debugging_service(self, sandbox_id: str):
        return self.build_route(
            "spaces/{self._space}/sandbox/{sandbox_id}/debuggingservice".format(**locals())
        )
