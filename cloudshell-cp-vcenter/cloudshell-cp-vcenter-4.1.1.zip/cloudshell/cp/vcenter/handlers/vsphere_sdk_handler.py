from __future__ import annotations

from logging import Logger
from typing import Union

import attr
from packaging import version

from cloudshell.cp.core.reservation_info import ReservationInfo

from cloudshell.cp.vcenter.exceptions import (
    TagFaultException,
    VSphereAPIAlreadyExistsException,
    VSphereAPINotFoundException,
)
from cloudshell.cp.vcenter.handlers.folder_handler import FolderHandler
from cloudshell.cp.vcenter.handlers.network_handler import (
    DVPortGroupHandler,
    NetworkHandler,
)
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vcenter_tag_handler import VCenterTagsManager
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.handlers.vsphere_api_handler import VSphereAutomationAPI
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig

OBJECTS_WITH_TAGS = Union[VmHandler, FolderHandler, NetworkHandler, DVPortGroupHandler]


@attr.s(auto_attribs=True, slots=True, frozen=True)
class VSphereSDKHandler:
    _vsphere_client: VSphereAutomationAPI
    _tags_manager: VCenterTagsManager | None
    _logger: Logger

    # From this version vCenter has vSphere Automation API that allows to work with tags
    VCENTER_VERSION = "6.5.0"

    POSSIBLE_TYPES = [
        "Network",
        "HostNetwork",
        "OpaqueNetwork",
        "DistributedVirtualPortgroup",
        "VirtualMachine",
        "Folder",
    ]

    @classmethod
    def from_config(
        cls,
        resource_config: VCenterResourceConfig,
        reservation_info: ReservationInfo,
        logger: Logger,
    ) -> VSphereSDKHandler | None:
        si = SiHandler.from_config(resource_config, logger)
        if version.parse(si.vc_version) >= version.parse(cls.VCENTER_VERSION):
            logger.info("Initializing vSphere API client.")
            vsphere_client = VSphereAutomationAPI(
                address=resource_config.address,
                username=resource_config.user,
                password=resource_config.password,
            )
            vsphere_client.connect()
            if reservation_info is not None:
                tags_manager = VCenterTagsManager(
                    resource_config=resource_config, reservation_info=reservation_info
                )
            else:
                tags_manager = None
            return cls(vsphere_client, tags_manager, logger)
        else:
            logger.warning(f"Tags available only from vCenter {cls.VCENTER_VERSION}")
            return

    def _get_all_categories(self) -> dict[str:str]:
        """Get all existing categories."""
        result = {}
        categories = self._vsphere_client.get_category_list()
        if len(categories) > 0:
            self._logger.debug("List of all existing categories user has access to...")
            for category_id in categories:
                category_info = self._vsphere_client.get_category_info(category_id)
                self._logger.debug(
                    f"CategoryName: {category_info['name']}, "
                    f"CategoryID: {category_info['id']}"
                )
                result.update({category_info["name"]: category_info["id"]})
        else:
            self._logger.info("No Tag Category Found...")

        return result

    def _get_or_create_tag_category(self, name: str) -> str:
        """Create a category or return an existing one.

        Note: User who invokes this needs create category privilege
        """
        try:
            category_id = self._vsphere_client.create_category(name)
        except VSphereAPIAlreadyExistsException:
            self._logger.debug(f"Tag Category {name} already exists.")
            category_id = self._get_all_categories().get(name)
            if category_id is None:
                raise TagFaultException("Error during tag category creation.")

        return category_id

    def create_categories(self, custom_categories: list | None = None):
        """Create all Default and Custom Tag Categories."""
        for tag_category in vars(VCenterTagsManager.DefaultTagNames):
            if not tag_category.startswith("__"):
                self._get_or_create_tag_category(
                    name=getattr(VCenterTagsManager.DefaultTagNames, tag_category)
                )

        if custom_categories:
            for custom_category in custom_categories:
                self._get_or_create_tag_category(name=custom_category)

    def _get_all_tags(self, category_id: str) -> dict[str:str]:
        """Get all existing tags for the given category.."""
        result = {}
        try:
            tags = self._vsphere_client.get_all_category_tags(category_id=category_id)
            if len(tags) > 0:
                self._logger.debug("List of all existing tags user has access to...")
                for tag_id in tags:
                    tag_info = self._vsphere_client.get_tag_info(tag_id)
                    self._logger.debug(
                        f"TagName: {tag_info['name']}, TagID: {tag_info['id']}"
                    )
                    result.update({tag_info["name"]: tag_info["id"]})
            else:
                self._logger.info("No Tag Found...")
        except VSphereAPINotFoundException as err:
            raise TagFaultException(err)
        else:
            return result

    def _get_or_create_tag(self, name: str, category_id: str) -> str:
        """Create a Tag."""
        try:
            tag_id = self._vsphere_client.create_tag(name=name, category_id=category_id)
            if tag_id is None:
                raise TagFaultException("Error during tag creation.")
        except VSphereAPIAlreadyExistsException as err:
            self._logger.debug(err)
            tag_id = self._get_all_tags(category_id=category_id).get(name)
        except VSphereAPINotFoundException as err:
            raise TagFaultException(err)

        return tag_id

    def _create_multiple_tag_association(
        self, obj: OBJECTS_WITH_TAGS, tag_ids: list[str]
    ) -> None:
        """Attach tags."""
        object_id, object_type = self._get_object_id_and_type(obj)
        self._vsphere_client.attach_multiple_tags_to_object(
            tag_ids=tag_ids, obj_id=object_id, obj_type=object_type
        )

    def assign_tags(
        self, obj: OBJECTS_WITH_TAGS, tags: dict[str:str] | None = None
    ) -> None:
        """Get/Create tags and assign to provided vCenter object."""
        if not tags:
            tags = self._tags_manager.get_default_tags()

        tag_ids = []
        for category_name, tag in tags.items():
            category_id = self._get_or_create_tag_category(name=category_name)
            tag_id = self._get_or_create_tag(name=tag, category_id=category_id)
            tag_ids.append(tag_id)

        self._create_multiple_tag_association(obj=obj, tag_ids=tag_ids)

    def _get_attached_tags(self, obj: OBJECTS_WITH_TAGS) -> list[str]:
        """Determine all tags attached to vCenter object."""
        object_id, object_type = self._get_object_id_and_type(obj)
        tag_ids = self._vsphere_client.list_attached_tags(
            obj_id=object_id, obj_type=object_type
        )
        return tag_ids

    def _delete_tag_category(self, category_id):
        """Delete an existing tag category.

        User who invokes this API needs delete privilege on the tag category.
        """
        try:
            self._vsphere_client.delete_category(category_id)
        except VSphereAPINotFoundException as err:
            self._logger.debug(err)

    def _delete_tag(self, tag_id: str) -> None:
        """Delete an existing tag.

        User who invokes this API needs delete privilege on the tag.
        """
        try:
            self._vsphere_client.delete_tag(tag_id)
        except VSphereAPINotFoundException as err:
            self._logger.debug(err)

    def delete_tags(self, obj):
        """Delete tags if it used ONLY in current reservation."""
        tag_to_objects_mapping = {}
        pattern_objects_list = None
        for tag_id in self._get_attached_tags(obj=obj):
            tag_info = self._vsphere_client.get_tag_info(tag_id)
            category_info = self._vsphere_client.get_category_info(
                tag_info["category_id"]
            )
            self._logger.debug(f"TagID: {tag_id}, Category: {category_info['name']}")
            if category_info["name"] == VCenterTagsManager.DefaultTagNames.sandbox_id:
                try:
                    pattern_objects_list = sorted(
                        self._vsphere_client.list_attached_objects(tag_id=tag_id),
                        key=lambda attached_object: attached_object["id"],
                    )

                    self._logger.debug(f"TagID to delete: {tag_id}")
                    self._delete_tag(tag_id)
                except VSphereAPINotFoundException:
                    self._logger.debug(f"Pattern TagID {tag_id} doesn't exist.")
                    break
            else:
                try:
                    candidate_objects_list = sorted(
                        self._vsphere_client.list_attached_objects(tag_id=tag_id),
                        key=lambda attached_object: attached_object["id"],
                    )

                    tag_to_objects_mapping.update({tag_id: candidate_objects_list})
                except VSphereAPINotFoundException:
                    self._logger.debug(f"Candidate TagID {tag_id} doesn't exist.")

        for tag_id, objects_list in tag_to_objects_mapping.items():
            if objects_list == pattern_objects_list:
                self._logger.debug(f"TagID to delete: {tag_id}")
                self._delete_tag(tag_id)

    def _get_object_id_and_type(self, obj: OBJECTS_WITH_TAGS) -> tuple[str, str]:
        object_id = obj._moId
        object_type = obj._wsdl_name
        self._logger.debug(f"Object type: {object_type}, Object ID: {object_id}")
        return object_id, object_type
