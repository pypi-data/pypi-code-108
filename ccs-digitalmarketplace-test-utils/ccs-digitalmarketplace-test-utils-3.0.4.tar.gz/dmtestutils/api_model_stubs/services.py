
from .base import BaseAPIModelStub

__all__ = [
    "ArchivedServiceStub",
    "DraftServiceStub",
    "ServiceStub",
]


class ServicesStubsBase(BaseAPIModelStub):
    resource_name = "services"
    default_data = {
        "id": 1010101010,
        "copiedToFollowingFramework": False,
        "frameworkSlug": "g-cloud-13",
        "frameworkFramework": "g-cloud",
        "frameworkFamily": "g-cloud",
        "frameworkName": "G-Cloud 13",
        "frameworkStatus": "open",
        "lot": "cloud-software",
        "lotSlug": "cloud-software",
        "lotName": "Cloud software",
        "serviceName": "I run a service that does a thing",
        "status": "not-submitted",
        "supplierId": 8866655,
        "supplierName": "Kev's Pies",
        "createdAt": "2017-04-07T12:34:00.000000Z",
        "updatedAt": "2017-04-07T12:34:00.000000Z",
    }
    optional_keys = (
        ("id", "serviceId"),
        ("id", "service_id"),
        ("frameworkFamily", "framework_family"),
        ("frameworkFramework", "framework_framework"),
        ("frameworkName", "framework_name"),
        ("frameworkSlug", "framework_slug"),
        ("lotSlug", "lot_slug"),
        ("lotName", "lot_name"),
        ("serviceName", "service_name"),
        ("supplierId", "supplier_id"),
        ("supplierName", "supplier_name"),
        ("createdAt", "created_at"),
        ("updatedAt", "updated_at"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.response_data["links"] = self._format_values(self.links)

        if (
            ("framework_slug" in kwargs or "frameworkSlug" in kwargs)
            and ("framework_name" not in kwargs and "frameworkName" not in kwargs)
            and ("framework_family" not in kwargs and "frameworkFamily" not in kwargs)
        ):
            self.response_data.update(
                self._format_framework(self.response_data["frameworkSlug"], new_style=False, old_style=True)
            )


class ArchivedServiceStub(ServicesStubsBase):
    links = {
        "self": "http://127.0.0.1:5000/archived-services/{id}",
    }

    def __init__(self, **kwargs):
        service_id = self.default_data["id"]
        service_id = kwargs.pop("service_id", service_id)
        service_id = kwargs.pop("serviceId", service_id)
        kwargs.setdefault("id", 1234)
        super().__init__(**kwargs)
        self.response_data["id"] = service_id


class DraftServiceStub(ServicesStubsBase):
    links = {
        "self": "http://127.0.0.1:5000/draft-services/{id}",
        "publish": "http://127.0.0.1:5000/draft-services/{id}/publish",
        "complete": "http://127.0.0.1:5000/draft-services/{id}/complete",
        "copy": "http://127.0.0.1:5000/draft-services/{id}/copy",
    }
    optional_keys = (
        ("frameworkFamily", "framework_family"),
        ("frameworkFramework", "framework_framework"),
        ("frameworkName", "framework_name"),
        ("frameworkSlug", "framework_slug"),
        ("lotSlug", "lot_slug"),
        ("lotName", "lot_name"),
        ("serviceId", "service_id"),
        ("serviceName", "service_name"),
        ("supplierId", "supplier_id"),
        ("supplierName", "supplier_name"),
        ("createdAt", "created_at"),
        ("updatedAt", "updated_at"),
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", 1234)
        super().__init__(**kwargs)


class ServiceStub(ServicesStubsBase):
    links = {
        "self": "http://127.0.0.1:5000/services/{id}",
    }

    def __init__(self, **kwargs):
        if "id" in kwargs:
            del kwargs["id"]
        super().__init__(**kwargs)
