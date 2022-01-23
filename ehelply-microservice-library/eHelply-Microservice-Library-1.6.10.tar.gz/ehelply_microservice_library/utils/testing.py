import asyncio

from ehelply_microservice_library.service_bootstrap import ServiceBootstrap

from fastapi.testclient import TestClient

from typing import Type, List, Optional

import json
import os
from pathlib import Path
from pydantic import BaseModel


class TestClientSingleton:
    test_client: Optional[TestClient] = None


class TestHeaders(BaseModel):
    access_token: str
    secret_token: str
    project_uuid: str

    def to_client_headers(self) -> dict:
        return {
            "ehelply-project": self.project_uuid,
            "x-access-token": self.access_token,
            "x-secret-token": self.secret_token
        }


def make_test_client(service: Type[ServiceBootstrap], additional_facts: List[str] = None) -> TestClient:
    if TestClientSingleton.test_client:
        return TestClientSingleton.test_client

    if not additional_facts:
        additional_facts = []

    class ServiceTest(service):
        def if_dev_launch_dev_server(self) -> bool:
            return False

        def after_fast_api(self):
            asyncio.run(super().startup_event())

        def get_fact_subscriptions(self) -> List[str]:
            return super().get_fact_subscriptions() + additional_facts

    service = ServiceTest()

    app = service.fastapi_driver.instance

    client = TestClient(app)

    TestClientSingleton.test_client = client

    return client


def make_test_headers(credentials_type: str = "") -> TestHeaders:
    root_path = Path(os.getcwd())

    if len(credentials_type) > 0:
        credentials_type = "." + credentials_type

    credentials_file = Path(root_path).resolve().joinpath(f"credentials.testing{credentials_type}.json")

    try:
        with open(str(credentials_file)) as file:
            return TestHeaders(**json.load(file))
    except:
        raise Exception("Invalid credentials file")
