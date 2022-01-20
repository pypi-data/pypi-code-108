# -*- coding: utf-8 -*-
from .base import RequestAPI


class CollectionsAPI(object):
    def __init__(self, client):
        from . import conf

        self.client = client
        self.host = "" or conf.HOST.format(api_name="bk-apigateway")

        self.sync_api = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/sync/")

        self.sync_stage = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/stages/sync/")

        self.sync_resources = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resources/sync/")

        self.create_resource_version = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/")

        self.sync_access_strategy = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/access_strategies/sync/")

        self.apply_permissions = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/permissions/apply/")

        self.get_apigw_public_key = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/public_key/")

        self.get_latest_resource_version = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/latest/")

        self.release = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/release/")

        self.grant_permissions = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/permissions/grant/")

        self.import_resource_docs_by_archive = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource-docs/import/by-archive/")

        self.import_resource_docs_by_swagger = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource-docs/import/by-swagger/")

        self.add_related_apps = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/related-apps/")

        self.revoke_permissions = RequestAPI(client=self.client, method="DELETE", host=self.host, path="/api/v1/apis/{api_name}/permissions/revoke/")
