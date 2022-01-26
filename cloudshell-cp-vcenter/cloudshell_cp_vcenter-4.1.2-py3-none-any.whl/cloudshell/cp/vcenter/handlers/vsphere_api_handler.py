from __future__ import annotations

import ssl
from abc import abstractmethod

import attr
import requests
import urllib3

from cloudshell.cp.vcenter.exceptions import (
    TagFaultException,
    VSphereAPIAlreadyExistsException,
    VSphereAPIConnectionException,
    VSphereAPINotFoundException,
)
from cloudshell.cp.vcenter.models.vsphere_tagging import CategorySpec, TagSpec


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BaseAPIClient:
    address: str
    username: str
    password: str
    session: requests.Session = requests.Session()
    scheme: str = "https"
    port: int = 443
    verify_ssl: bool = ssl.CERT_NONE

    def __attrs_post_init__(self):
        self.session.verify = self.verify_ssl
        self.session.headers.update({"Content-Type": "application/json"})
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @abstractmethod
    def _base_url(self):
        pass

    def _do_get(
        self, path: str, raise_for_status: bool = True, **kwargs: dict
    ) -> requests.Response:
        """Basic GET request client method."""
        url = f"{self._base_url()}/{path}"
        res = self.session.get(url=url, **kwargs)
        raise_for_status and res.raise_for_status()
        return res

    def _do_post(
        self, path: str, raise_for_status: bool = True, **kwargs: dict
    ) -> requests.Response:
        """Basic POST request client method."""
        url = f"{self._base_url()}/{path}"
        res = self.session.post(url=url, **kwargs)
        raise_for_status and res.raise_for_status()
        return res

    def _do_put(
        self, path: str, raise_for_status: bool = True, **kwargs: dict
    ) -> requests.Response:
        """Basic PUT request client method."""
        url = f"{self._base_url()}/{path}"
        res = self.session.put(url=url, **kwargs)
        raise_for_status and res.raise_for_status()
        return res

    def _do_delete(
        self, path: str, raise_for_status: bool = True, **kwargs: dict
    ) -> requests.Response:
        """Basic DELETE request client method."""
        url = f"{self._base_url()}/{path}"
        res = self.session.delete(url=url, **kwargs)
        raise_for_status and res.raise_for_status()
        return res


class VSphereAutomationAPI(BaseAPIClient):
    class Decorators:
        @classmethod
        def get_data(cls, decorated):
            def inner(*args, **kwargs):
                return decorated(*args, **kwargs).json()["value"]

            return inner

    def _base_url(self):
        return f"{self.scheme}://{self.address}:{self.port}/rest/com/vmware/cis"

    def connect(self):
        """"""
        try:
            return self._do_post(path="session")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise VSphereAPIConnectionException(
                    "Connection failed. Please, check credentials."
                )
            elif err.response.status_code == 503:
                raise VSphereAPIConnectionException(
                    "vSphere Automation API service unavailable."
                )

    @Decorators.get_data
    def create_category(self, name: str):
        """Create category.

        Note: you need the create category privilege.
        """
        try:
            category_spec = {"create_spec": CategorySpec(name=name).to_dict()}
            res = self._do_post(path="tagging/category", json=category_spec)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 400:
                raise VSphereAPIAlreadyExistsException(
                    f"Category {name} already exists."
                )
            elif err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to create a category.")
        else:
            return res

    @Decorators.get_data
    def get_category_list(self):
        """Get list of all existed category.

        Note: The list will only contain those categories
              for which you have read privileges.
        """
        return self._do_get(path="tagging/category")

    @Decorators.get_data
    def get_category_info(self, category_id: str):
        """Fetches the category information for the given category identifier.

        Note: you need the read privilege on the category.
        """
        try:
            res = self._do_get(path=f"tagging/category/id:{category_id}")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to read the category.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Category with ID {category_id} doesn't exist."
                )
        else:
            return res

    def delete_category(self, category_id: str):
        """Deletes an existing category.

        Note: you need the delete privilege on the category.
        """
        try:
            self._do_delete(path=f"tagging/category/id:{category_id}")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise TagFaultException("User can not be authenticated..")
            elif err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to delete the category.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Category with ID {category_id} doesn't exist."
                )

    @Decorators.get_data
    def create_tag(self, name: str, category_id: str):
        """Creates a tag.

        Note: you need the create tag privilege on the input category.
        """
        try:
            tag_spec = {
                "create_spec": TagSpec(name=name, category_id=category_id).to_dict()
            }
            res = self._do_post(path="tagging/tag", json=tag_spec)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 400:
                raise VSphereAPIAlreadyExistsException(
                    f"Tag {name} already exists in Category ID {category_id}."
                )
            elif err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to create tag.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Category with ID {category_id} doesn't exist."
                )
        else:
            return res

    @Decorators.get_data
    def get_all_category_tags(self, category_id: str):
        """Get all tags for the given category.

        Note: you need the read privilege on the given category
              and the individual tags in that category.
        """
        try:
            res = self._do_post(
                path=f"tagging/tag/id:{category_id}?~action=list-tags-for-category"
            )

        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to read the category.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Category with ID {category_id} doesn't exist."
                )
        else:
            return res

    @Decorators.get_data
    def get_tag_info(self, tag_id: str):
        """Get tag information for the given tag identifier.

        Note: you need the read privilege on the tag in order to view the tag info.
        """
        try:
            res = self._do_get(path=f"tagging/tag/id:{tag_id}")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to read the tag.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Tag with ID {tag_id} doesn't exist."
                )
        else:
            return res

    def attach_multiple_tags_to_object(
        self, obj_id: str, obj_type: str, tag_ids: list[str]
    ):
        """Attaches the given tags to the input object.

        Note: you need the read privilege on the object and
              the attach tag privilege on each tag.
        """
        create_association = {
            "object_id": {"id": obj_id, "type": obj_type},
            "tag_ids": tag_ids,
        }
        try:
            self._do_post(
                path="tagging/tag-association?~action=attach-multiple-tags-to-object",
                json=create_association,
            )
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise TagFaultException("User can not be authenticated..")
            elif err.response.status_code == 403:
                raise TagFaultException(
                    f"Not enough privileges to read the object {obj_type}."
                )

    @Decorators.get_data
    def list_attached_tags(self, obj_id: str, obj_type: str):
        """Get the list of tags attached to the given object.

        Note: you need the read privilege on the input object.
              The list will only contain those tags
              for which you have the read privileges.
        """
        try:
            get_association = {"object_id": {"id": obj_id, "type": obj_type}}
            res = self._do_post(
                path="tagging/tag-association?~action=list-attached-tags",
                json=get_association,
            )
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise TagFaultException("User can not be authenticated..")
            elif err.response.status_code == 403:
                raise TagFaultException(
                    f"Not enough privileges to read the object {obj_type}."
                )
        else:
            return res

    @Decorators.get_data
    def list_attached_objects(self, tag_id: str):
        """Get the list of attached objects for the given tag.

        Note: you need the read privilege on the input tag.
              Only those objects for which you have the read privilege will be returned.
        """
        try:
            res = self._do_post(
                path=f"tagging/tag-association/id:{tag_id}?~action=list-attached-objects",  # noqa: E501
            )
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise TagFaultException("User can not be authenticated..")
            elif err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to read the tag.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Tag with ID {tag_id} doesn't exist."
                )
        else:
            return res

    def delete_tag(self, tag_id: str):
        """Deletes an existing tag.

        Note: you need the delete privilege on the tag.
        """
        try:
            self._do_delete(path=f"tagging/tag/id:{tag_id}")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise TagFaultException("User can not be authenticated..")
            elif err.response.status_code == 403:
                raise TagFaultException("Not enough privileges to delete the tag.")
            elif err.response.status_code == 404:
                raise VSphereAPINotFoundException(
                    f"Tag with ID {tag_id} doesn't exist."
                )
