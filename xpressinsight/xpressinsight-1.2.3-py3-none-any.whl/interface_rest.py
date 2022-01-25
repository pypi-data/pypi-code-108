"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Online interface definition.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""
import os
from typing import Dict, List, Optional, Union, Type
from datetime import datetime
from xpressinsight.types import XiEnum

from xpressinsight.interface import (
    _raise_interface_error,
    Attachment,
    AttachmentRules,
    AttachStatus,
    AttachTag,
    AttachTagUsage,
    ItemInfo,
    ExecMode,
    AppInterface,
    Metric,
    ObjSense,
)
import xpressinsight.rest as xi_rest

ERROR_MSG_PROD_MODE = 'The method "{}" cannot be used in production mode.'
ATTACH_STATUS_PREFIX = "INSIGHT_ATTACH_"


class RequestStatus(XiEnum):
    """
    Indicates the status of the most recent attempt to call a generic AppInterface function.

    Attributes
    ----------
    OK: int
        The operation completed successfully.
    ERROR: int
        An error occurred.

    Notes
    -----
    This enum is only used internally.
    """

    OK = 0
    ERROR = 1


def parse_status_str(status_str: str, prefix: str, enum_type: Type[XiEnum]) -> Union[RequestStatus, AttachStatus]:
    """
    Convert a string like `"INSIGHT_OK"` into enum value `RequestStatus.OK`.
    """

    #
    if not status_str.startswith(prefix):
        raise ValueError(f'Invalid {enum_type.__name__} string prefix: "{status_str}". Expected: "{prefix}".')

    #
    short_status_str = status_str[len(prefix):]

    if short_status_str not in enum_type.__members__:
        raise ValueError(f'Unknown {enum_type.__name__}: "{status_str}".')

    return enum_type[short_status_str]


def parse_request_status(request_status_str: str) -> RequestStatus:
    """
    Convert a string like `"INSIGHT_OK"` into enum value `RequestStatus.OK`.
    """
    return parse_status_str(request_status_str, "INSIGHT_", RequestStatus)


def parse_attach_status(attach_status_str: str) -> AttachStatus:
    """
    Convert a string like `"INSIGHT_ATTACH_INVALID_FILENAME"` into enum value `AttachStatus.INVALID_FILENAME`.
    """
    return parse_status_str(attach_status_str, "INSIGHT_ATTACH_", AttachStatus)


#
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def _attachment_from_dict(attachment: Dict, attach_status: AttachStatus = AttachStatus.OK) -> Optional[Attachment]:
    if attach_status != AttachStatus.OK:
        return None

    return Attachment(
        filename=attachment["filename"],
        description=attachment["description"],
        tags=attachment["tags"],
        size=attachment["size"],
        last_modified_user=attachment["lastModifiedUser"],
        last_modified_date=datetime.strptime(attachment["lastModifiedDate"], DATETIME_FORMAT),
        hidden=attachment["hidden"],
    )


def _item_info_from_dict(item_info: Dict) -> ItemInfo:
    return ItemInfo(
        id=item_info["id"],
        type=item_info["type"],
        name=item_info["name"],
        path=item_info["path"],
        parent_path=item_info["parentpath"]
    )


class AppRestInterface(AppInterface):
    """
    This class represents the Xpress Insight application interface. Use this interface to access attachments
    and meta data like the scenario ID.
    """

    #
    def __init__(
            self,
            rest_port: int,
            rest_token: str,
            app_id: str = "",
            app_name: str = "",
            scenario_id: str = "",
            scenario_name: str = "",
            scenario_path: str = "",
            exec_mode: str = ExecMode.NONE,  #
            test_mode: bool = False,
            test_attach_dir: str = "",
            test_cfile_path: str = "",
            #
            force_wdir_to_temp: bool = False,  #
            #
            tmp_dir: str = "",  #
            work_dir: str = os.path.join("work_dir", "insight"),
    ) -> None:

        super().__init__(app_id=app_id,
                         app_name=app_name,
                         scenario_id=scenario_id,
                         scenario_name=scenario_name,
                         scenario_path=scenario_path,
                         exec_mode=exec_mode,
                         test_mode=test_mode,
                         test_attach_dir=test_attach_dir,
                         test_cfile_path=test_cfile_path,
                         force_wdir_to_temp=force_wdir_to_temp,
                         tmp_dir=tmp_dir,
                         work_dir=work_dir)

        self._init_rest(rest_port, rest_token)
        self._attach_status = None

    def _init_rest(self, port: int, token: str):
        configuration = xi_rest.Configuration(
            host="http://localhost:{}".format(port),
            api_key={"token": "token={}".format(token)},
        )

        api_client = xi_rest.ApiClient(configuration)
        self._api = xi_rest.DefaultApi(api_client)

        #

    @property
    def work_dir(self) -> str:

        return self._work_dir

    def delete_work_dir(self):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('delete_work_dir'))

    @property
    def test_mode(self) -> bool:

        return self._test_mode

    #
    @property
    def exec_mode(self) -> str:

        return self._exec_mode

    #
    @property
    def app_id(self) -> str:

        return self._api.app_id_get()

    #
    @property
    def app_name(self) -> str:

        return self._api.app_name_get()

    #
    @property
    def username(self) -> str:

        return self._api.username_get()

    #

    #

    #
    @property
    def attach_status(self) -> AttachStatus:

        return self._attach_status

    #
    #

    #
    def list_attach_tags(self) -> List[AttachTag]:

        result = self._api.attachments_tags_get()
        self._attach_status = parse_attach_status(result["status"])
        return [
            AttachTag(
                name=tag["name"],
                description=tag["description"],
                mandatory=tag["mandatory"],
                usage=AttachTagUsage(tag["usage"]),
            )
            for tag in result["tags"]
        ]

    #
    #
    def get_scen_attach(self, filename: str, scenario_path: str = None) -> None:

        if scenario_path is None:
            scenario_path = ""

        attach_status_str = self._api.scenario_attachment_get(filename, scenariopath=scenario_path)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    #
    def put_scen_attach(self, filename: str, overwrite: bool = True) -> None:

        attach_status_str = self._api.scenario_attachment_put(filename, overwrite)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    def delete_scen_attach(self, filename: str) -> None:

        attach_status_str = self._api.scenario_attachment_delete(filename)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    def rename_scen_attach(self, old_name: str, new_name: str) -> None:

        attach_status_str = self._api.scenario_attachment_rename(old_name, new_name)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    def set_scen_attach_desc(self, filename: str, description: str) -> None:

        attach_status_str = self._api.scenario_attachment_description_put(
            filename, description=description
        )
        self._attach_status = parse_attach_status(attach_status_str)

    #
    def set_scen_attach_tags(self, filename: str, tags: List[str]) -> None:

        attach_status_str = self._api.scenario_attachment_tags_put(filename, tags=tags)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    def set_scen_attach_hidden(self, filename: str, hidden: bool) -> None:

        attach_status_str = self._api.scenario_attachment_hidden_put(filename, hidden=hidden)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    #
    def list_scen_attach(self, scenario_path: str = None) -> List[Attachment]:

        return self.list_scen_attach_by_tag("", scenario_path)

    #
    #
    #
    def list_scen_attach_by_tag(
            self, tag: str, scenario_path: str = None
    ) -> List[Attachment]:

        if scenario_path is None:
            scenario_path = ""

        result = self._api.scenario_attachments_list_get(tag=tag, scenariopath=scenario_path)
        self._attach_status = parse_attach_status(result["status"])
        return [_attachment_from_dict(a) for a in result["attachments"]]

    #
    def scen_attach_info(self, filename: str) -> Optional[Attachment]:

        result = self._api.scenario_attachment_info_get(filename)
        self._attach_status = parse_attach_status(result["status"])

        #
        #
        #
        return _attachment_from_dict(result["attachment"], self._attach_status)

    #
    def get_app_attach(self, filename: str) -> None:

        attach_status_str = self._api.app_attachment_get(filename)
        self._attach_status = parse_attach_status(attach_status_str)

    #
    def list_app_attach(self) -> List[Attachment]:

        tag = ""
        return self.list_app_attach_by_tag(tag)

    #
    def list_app_attach_by_tag(self, tag: str) -> List[Attachment]:

        result = self._api.app_attachments_list_get(tag)
        self._attach_status = parse_attach_status(result["status"])
        return [_attachment_from_dict(a) for a in result["attachments"]]

    #
    def app_attach_info(self, filename: str) -> Optional[Attachment]:

        result = self._api.app_attachment_info_get(filename)
        self._attach_status = parse_attach_status(result["status"])
        return _attachment_from_dict(result["attachment"], self.attach_status)

    #
    def get_attachs_by_tag(self, tag: str) -> Optional[List[Attachment]]:

        result = self._api.attachments_tags_bytag_get(tag)
        self._attach_status = parse_attach_status(result["status"])
        return [_attachment_from_dict(a) for a in result["attachments"]]

    #
    def get_attach_by_tag(self, tag: str) -> Optional[Attachment]:

        attachments = self.get_attachs_by_tag(tag)
        if len(attachments) == 1:
            return attachments[0]
        elif len(attachments) == 0:
            return None
        else:
            self._attach_status = AttachStatus.TOO_MANY
            return None

    #
    def get_attach_filenames_by_tag(self, tag: str) -> List[str]:

        attachments = self.get_attachs_by_tag(tag)
        return [a.filename for a in attachments]

    #
    def get_attach_rules(self) -> AttachmentRules:
        rules = self._api.attachments_rules_get()

        return AttachmentRules(
            max_size=rules["maxsize"],
            max_attach_count=rules["maxattachcount"],
            max_filename_len=rules["maxfilenamelen"],
            invalid_filename_chars=rules["invalidfilenamechars"],
            max_description_len=rules["maxdescriptionlen"],
        )

    def get_item_info(self, path: str) -> ItemInfo:
        result = self._api.repository_item_info_get(path)
        status = parse_request_status(result["status"])

        if status != RequestStatus.OK:
            _raise_interface_error(f"Could not get item info. (Status: {status})")

        return _item_info_from_dict(result["item_info"])

    def get_item_infos(self, folder_path: str) -> List[ItemInfo]:
        result = self._api.repository_item_infos_list_get(folder_path)
        status = parse_request_status(result["status"])

        if status != RequestStatus.OK:
            _raise_interface_error(f"Could not get item infos. (Status: {status})")

        return [_item_info_from_dict(item_info) for item_info in result["item_infos"]]

    def add_item_info(self, item_info: ItemInfo) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('add_item_info'))

    def clear_item_infos(self) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('clear_item_infos'))

    #

    #

    @property
    def scenario_id(self):
        return self._api.scenario_id_get()

    @property
    def scenario_name(self) -> str:
        return self._api.scenario_name_get()

    @property
    def scenario_path(self) -> str:
        return self._api.scenario_path_get()

    @property
    def test_cfile_path(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_cfile_path getter'))

    @test_cfile_path.setter
    def test_cfile_path(self, cfile_path: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_cfile_path setter'))

    @property
    def test_attach_dir(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_attach_dir getter'))

    @test_attach_dir.setter
    def test_attach_dir(self, attach_dir: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_attach_dir setter'))

    @property
    def test_app_attach_dir(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_app_attach_dir getter'))

    @test_app_attach_dir.setter
    def test_app_attach_dir(self, app_attach_dir: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_app_attach_dir setter'))

    @property
    def test_scen_attach_dir(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_scen_attach_dir getter'))

    @test_scen_attach_dir.setter
    def test_scen_attach_dir(self, scen_attach_dir: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('test_scen_attach_dir setter'))

    def set_attach_tags(self, new_tags: List[AttachTag]):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('set_attach_tags'))

    def set_attach_rules(self, new_rules: AttachmentRules):
        raise RuntimeError(ERROR_MSG_PROD_MODE.format('set_attach_rules'))

    def update(self, metric: Metric, value: Union[float, int, ObjSense]) -> None:
        float_value = value.value if isinstance(value, ObjSense) else float(value)
        self._api.progress_update(metric=metric.value, value=float_value)

    def reset_progress(self) -> None:
        self._api.progress_reset()
