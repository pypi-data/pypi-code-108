"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Offline interface definition.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import copy  #
import dataclasses
import datetime
import os
import pickle  #
import shutil
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union

from xpressinsight.interface import (
    _raise_interface_error,
    _raise_runtime_error,
    _raise_io_error,
    Attachment,
    AttachmentRules,
    AttachStatus,
    AttachTag,
    AttachTagUsage,
    AttachType,
    AttachUpdateType,
    AppInterface,
    ItemInfo,
    Metric,
    ObjSense,
)

from xpressinsight.exec_mode import ExecMode
from xpressinsight.types import check_simple_python_type
from xpressinsight.repository_path import RepositoryPath


def sorted_by_key(d: Dict) -> List:
    """given a dictionary returns a list of (key, value) sorted by key"""

    return [v for (_, v) in sorted(d.items(), key=lambda kv: kv[0])]


#
ATTACH_DIR_RELATIVE_TO_INSTANCE_ROOT = ".mminsight/attach"


#
CFILE_NS = {"cf": "http://www.fico.com/xpress/optimization-modeler/model-companion"}


def write_attach_info(att: Attachment, filename: str, label: str = "attach") -> None:
    """Serializes an Attachment object to a file"""

    obj = {label: att}
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def read_attach_info(filename: str, label: str = "attach") -> Attachment:
    """Unserializes an Attachment object from a file"""
    with open(filename, "rb") as f:
        obj = pickle.load(f)

    attach: Attachment = obj[label]

    return attach


#
@dataclass
class XpriAttachment(Attachment):
    """All meta-data about an attachment. Updated as we make local changes"""

    #
    id: str = field(default="")

    #
    is_new_attachment: bool = field(default=False)

    is_content_modified: bool = field(default=False)

    #
    local_content_filename: str = field(default="")


#
@dataclass
class XpriAttachmentUpdate:
    """
    Record of an attachment being updated.
    Note: newly-created attachments are not recorded in xpri_attachmentupdate records.
    """

    #
    update_type: AttachUpdateType = field()

    attach_type: AttachType = field()

    attach_id: str = field(default="")

    #
    filename: str = field(default="")
    description: str = field(default="")
    tags: List[str] = field(default_factory=list)
    hidden: bool = field(default=False)
    size: int = field(default=0)
    local_content_filename: str = field(default="")


#
@dataclass
class XpriAttachmentsCache:
    """Attachments Cache"""

    #
    type: AttachType = field()  #

    #
    id: str = field(default="")

    #
    attachments: Dict[str, XpriAttachment] = field(default_factory=dict)

    #
    is_populated: bool = field(default=False)

    #
    single_file_tag_attachments: Dict[str, str] = field(default_factory=dict)


#
def read_attachment_tags_from_element(e: ElementTree.Element) -> Tuple[AttachTag, List[str]]:
    """This function converts xml.etree.ElementTree.Element to InsightAttachmentTag"""

    name = e.get("name", "")
    if name == "":
        raise ValueError("Attachment tag name cannot be empty")

    description = e.findtext("cf:description", "", CFILE_NS)

    mandatory_str = e.get("mandatory", "false")
    assert mandatory_str in ["true", "false"]
    mandatory = mandatory_str == "true"

    usage_str = e.get("usage", AttachTagUsage.MULTI_FILE.value)
    #
    usage = None
    if usage_str == "SINGLE_FILE":
        usage = AttachTagUsage.SINGLE_FILE
    elif usage_str == "MULTI_FILE":
        usage = AttachTagUsage.MULTI_FILE
    else:
        usage = AttachTagUsage(usage_str)

    attachments_e = e.findall("cf:attachments/cf:attachment", CFILE_NS)
    if attachments_e is None:
        attachments_e = []

    attachments = [a.text for a in attachments_e]

    return (AttachTag(name, description, mandatory, usage), attachments)


def read_attachment_tags_from_cfile(
        cfile_path: str,
) -> Tuple[Dict[str, AttachTag], Dict[str, List[str]]]:
    """This function reads a XML companion file and extracts all attachment tags"""

    #
    xpath = "cf:attachment-config/cf:attachment-tags/cf:attachment-tag"

    elements = ElementTree.parse(cfile_path).findall(xpath, CFILE_NS)

    ea = list(map(read_attachment_tags_from_element, elements))

    attach_tags = {attach_tag.name: attach_tag for (attach_tag, attachments) in ea}
    default_attach_tags = {
        attach_tag.name: attachments for (attach_tag, attachments) in ea
    }

    return attach_tags, default_attach_tags


class AppTestInterface(AppInterface):
    """
    This class represents the Xpress Insight application interface. Use this interface to access attachments
    and meta data like the scenario ID.
    """

    #
    def __init__(
            self,
            app_id: str = "",
            app_name: str = "",
            scenario_id: str = "",
            scenario_name: str = "",
            scenario_path: str = "",
            exec_mode: str = ExecMode.NONE,  #
            test_mode: bool = True,
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

        #

        #
        if self._scenario_id == "":
            self._scenario_id = "scenid"

        if self._scenario_name == "":
            self._scenario_name = "scenname"

        if self._scenario_path == "":
            self._scenario_path = "/appname/scenname"

        if self._app_id == "":
            self._app_id = "appid"

        if self._app_name == "":
            self._app_name = "appname"

        if self._force_wdir_to_temp:
            print("Setting working directory to {}".format(self._tmp_dir))
            self._work_dir = self._tmp_dir

        #
        #
        #
        #
        #
        #
        #
        self._scratch_dir = os.path.join(self._work_dir, ".mminsight")

        #
        self._has_fetched_user_details: bool = False  #
        self._username: str = "UNKNOWN"

        #

        #
        self._last_attach_id: int = 0

        #
        #
        #
        #
        self._attach_tags: Dict[
            str, AttachTag
        ] = {}  #

        #
        self._has_fetched_attach_tag_types: bool = False

        #
        #
        self._default_attach_tags: Dict[str, List[str]] = dict()

        #
        self._attachment_updates: List[XpriAttachmentUpdate] = []

        #
        self._attachment_filenames: Set[
            str
        ] = set()  #

        #
        #
        self._scen_attach_cache_map: Dict[str, XpriAttachmentsCache] = {}

        #
        self._test_mode_app_attach_dir: str = ""

        #
        self._test_mode_scen_attach_dir: str = ""

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)

        #
        self._app_attach_cache: XpriAttachmentsCache = XpriAttachmentsCache(
            type=AttachType.APP, id=self.app_id
        )

        #
        self._attach_rules: Optional[AttachmentRules] = None
        self._has_fetched_attach_rules: bool = False

        #

        #
        self._xpri_attach_stat: AttachStatus = AttachStatus.OK

        #
        #
        #
        self._item_infos_by_id: Dict[str, ItemInfo] = {}
        self._item_infos_by_path: Dict[str, ItemInfo] = {}

    @property
    def work_dir(self) -> str:
        return self._work_dir

    def delete_work_dir(self):
        if os.path.isdir(self.work_dir):
            print(f'Test mode: Deleting existing Insight working directory: "{self.work_dir}".')
            shutil.rmtree(self.work_dir)

    @property
    def test_mode(self) -> bool:
        return True

    #
    def _xpri_get_mminsight_scratch_dir(self) -> str:
        """Return path to scratch directory, creating it if necessary"""
        if not os.path.isdir(self._scratch_dir):
            os.makedirs(self._scratch_dir)
        return self._scratch_dir

    @property
    def exec_mode(self) -> str:

        return self._exec_mode

    #
    @property
    def app_id(self) -> str:

        return self._app_id

    #
    @property
    def app_name(self) -> str:

        return self._app_name

    #
    def _xpri_load_user_info(self):
        """Ensure that we've fetched the user details from the Insight server"""

        if not self._has_fetched_user_details:
            self._username = "Test User"
            self._has_fetched_user_details = True

    #
    @property
    def username(self) -> str:

        self._xpri_load_user_info()
        return self._username

    #

    #

    #
    @app_id.setter
    def app_id(self, new_app_id: str):

        self._app_id = new_app_id

    #
    @app_name.setter
    def app_name(self, new_app_name: str):

        self._app_name = new_app_name

    #
    @username.setter
    def username(self, new_username: str):

        self._username = new_username
        self._has_fetched_user_details = True

    #
    @exec_mode.setter
    def exec_mode(self, exec_mode: str):

        self._exec_mode = exec_mode

    @property
    def test_cfile_path(self) -> str:
        return self._test_cfile_path

    @test_cfile_path.setter
    def test_cfile_path(self, cfile_path: str):
        self._test_cfile_path = cfile_path

    @property
    def test_attach_dir(self) -> str:
        return self._test_attach_dir

    @test_attach_dir.setter
    def test_attach_dir(self, attach_dir: str):
        self._test_attach_dir = attach_dir

    @property
    def test_app_attach_dir(self) -> str:
        return self._test_mode_app_attach_dir

    #
    @test_app_attach_dir.setter
    def test_app_attach_dir(self, app_attach_dir: str):
        self._test_mode_app_attach_dir = app_attach_dir

    @property
    def test_scen_attach_dir(self) -> str:
        return self._test_mode_scen_attach_dir

    #
    @test_scen_attach_dir.setter
    def test_scen_attach_dir(self, scen_attach_dir: str):
        self._test_mode_scen_attach_dir = scen_attach_dir

    #
    def set_attach_tags(self, new_tags: List[AttachTag]):

        self._xpri_clear_attach_stat()

        new_attach_tags = {t.name: t for t in new_tags}
        self._attach_tags = copy.deepcopy(new_attach_tags)
        self._has_fetched_attach_tag_types = True

        self._xpri_set_attach_stat(AttachStatus.OK)

    #
    def set_attach_rules(self, new_rules: AttachmentRules):

        self._xpri_clear_attach_stat()

        self._attach_rules = copy.deepcopy(new_rules)
        self._has_fetched_attach_rules = True

        self._xpri_set_attach_stat(AttachStatus.OK)

    #
    def _xpri_clear_attach_stat(self) -> None:
        if self._xpri_attach_stat == AttachStatus.IN_PROGRESS:
            _raise_runtime_error("Already in attachment operation.")
        self._xpri_attach_stat = AttachStatus.IN_PROGRESS

    #
    def _xpri_set_attach_stat(self, new_stat: AttachStatus) -> None:
        if self._xpri_attach_stat != AttachStatus.IN_PROGRESS:
            _raise_runtime_error("Not in attachment operation.")
        if new_stat == AttachStatus.IN_PROGRESS:
            _raise_runtime_error("Invalid status passed to _xpri_set_attach_stat.")
        self._xpri_attach_stat = new_stat

    #
    @property
    def attach_status(self) -> AttachStatus:

        return self._xpri_attach_stat

    #
    #

    #
    def list_attach_tags(self) -> List[AttachTag]:

        self._xpri_clear_attach_stat()
        #
        if not self._xpri_load_attach_tags():
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return []
        else:
            #
            sorted_attach_tags = sorted_by_key(self._attach_tags)

            self._xpri_set_attach_stat(AttachStatus.OK)
            return sorted_attach_tags

    #
    #
    def get_scen_attach(self, filename: str, scenario_path: str = None) -> None:

        scenario_id = (
            self._scenario_id
            if scenario_path is None
            else self._xpri_get_scenario_id(scenario_path)
        )

        #
        self._xpri_ensure_scen_attach_cache_exists(scenario_id)

        self._xpri_get_attach(self._scen_attach_cache_map[scenario_id], filename)

    #
    #
    def put_scen_attach(self, filename: str, overwrite: bool = True) -> None:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        self._xpri_put_attach(
            self._scen_attach_cache_map[self._scenario_id], filename, overwrite
        )

    #
    def delete_scen_attach(self, filename: str) -> None:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        self._xpri_delete_attach(
            self._scen_attach_cache_map[self._scenario_id], filename
        )

    #
    def rename_scen_attach(self, old_name: str, new_name: str) -> None:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        self._xpri_rename_attach(
            self._scen_attach_cache_map[self._scenario_id], old_name, new_name
        )

    #
    def set_scen_attach_desc(self, filename: str, description: str) -> None:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        self._xpri_set_attach_desc(
            self._scen_attach_cache_map[self._scenario_id], filename, description
        )

    #
    def set_scen_attach_tags(self, filename: str, tags: List[str]) -> None:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        self._xpri_set_attach_tags(
            self._scen_attach_cache_map[self._scenario_id], filename, tags
        )

    #
    def set_scen_attach_hidden(self, filename: str, hidden: bool) -> None:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        self._xpri_set_attach_hidden(
            self._scen_attach_cache_map[self._scenario_id], filename, hidden
        )

    #
    def xpri_write_single_file_tag_scen_attach(self) -> None:
        """
        !@doc.autogen false
        ! Output names of scenario attachments with single-file tags within this cache
        ! (for testing purposes)
        """

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        #
        #
        #

    #
    #
    def list_scen_attach(self, scenario_path: str = None) -> List[Attachment]:

        scenario_id = (
            self._scenario_id
            if scenario_path is None
            else self._xpri_get_scenario_id(scenario_path)
        )

        #
        self._xpri_ensure_scen_attach_cache_exists(scenario_id)
        return self._xpri_list_attach(self._scen_attach_cache_map[scenario_id])

    #
    #
    def list_scen_attach_by_tag(
            self, tag: str, scenario_path: str = None
    ) -> List[Attachment]:

        scenario_id = (
            self._scenario_id
            if scenario_path is None
            else self._xpri_get_scenario_id(scenario_path)
        )

        #
        self._xpri_ensure_scen_attach_cache_exists(scenario_id)
        return self._xpri_list_attach_by_tag(
            self._scen_attach_cache_map[scenario_id], tag
        )

    #
    def scen_attach_info(self, filename: str) -> Optional[Attachment]:

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
        return self._xpri_get_attach_info(
            self._scen_attach_cache_map[self._scenario_id], filename
        )

    #
    def get_app_attach(self, filename: str) -> None:

        self._xpri_get_attach(self._app_attach_cache, filename)

    #
    def list_app_attach(self) -> List[Attachment]:

        return self._xpri_list_attach(self._app_attach_cache)

    #
    def list_app_attach_by_tag(self, tag: str) -> List[Attachment]:

        #
        return self._xpri_list_attach_by_tag(self._app_attach_cache, tag)

    #
    def app_attach_info(self, filename: str) -> Optional[Attachment]:

        return self._xpri_get_attach_info(self._app_attach_cache, filename)

    #
    def get_attachs_by_tag(self, tag: str) -> Optional[List[Attachment]]:

        return self._xpri_get_attachs_by_tag(tag)

    #
    def get_attach_by_tag(self, tag: str) -> Optional[Attachment]:

        return self._xpri_get_attach_by_tag(tag)

    #
    def get_attach_filenames_by_tag(self, tag: str) -> List[str]:

        return self._xpri_get_attach_filenames_by_tag(tag)

    #
    def get_attach_rules(self) -> AttachmentRules:

        self._xpri_load_attach_rules()
        return copy.deepcopy(self._attach_rules)

    #
    def get_item_info(self, path: str) -> ItemInfo:
        check_simple_python_type(path, 'path', str)

        #
        item_info = self._item_infos_by_id.get(path)

        if item_info is None:
            #
            parent_path = RepositoryPath(self.scenario_parent_path)
            search_path = RepositoryPath(self.scenario_path if path == '.' else path)
            norm_search_path_str = str(search_path.abspath(parent_path))
            item_info = self._item_infos_by_path.get(norm_search_path_str)

            if item_info is None:
                _raise_interface_error(f"Item with ID '{path}' or path '{norm_search_path_str}' was not found.")

        return dataclasses.replace(item_info)

    #
    def get_item_infos(self, folder_path: str) -> List[ItemInfo]:
        folder_item = self.get_item_info(self.scenario_parent_path if folder_path == "." else folder_path)

        if folder_item.type != 'FOLDER':
            _raise_interface_error("Item '" + folder_item.path + "' is not a folder.")

        #
        folder_item_path = folder_item.path + '/'

        return [dataclasses.replace(item)
                for item in self._item_infos_by_id.values()
                if item.parent_path == folder_item_path and item.id != folder_item.id]

    #
    def add_item_info(self, item_info: ItemInfo) -> None:
        check_simple_python_type(item_info, 'item_info', ItemInfo)

        #
        item_info = dataclasses.replace(item_info)
        item_info.normalize()

        if item_info.id in self._item_infos_by_id:
            raise KeyError(f'An ItemInfo with id {repr(item_info.id)} has already been added.')

        if item_info.path in self._item_infos_by_path:
            raise KeyError(f'An ItemInfo with path {repr(item_info.path)} has already been added.')

        self._item_infos_by_id[item_info.id] = item_info
        self._item_infos_by_path[item_info.path] = item_info

    #
    def clear_item_infos(self) -> None:
        self._item_infos_by_id: Dict[str, ItemInfo] = {}
        self._item_infos_by_path: Dict[str, ItemInfo] = {}

    def _fdelete(self, filename: str) -> bool:
        try:
            os.remove(filename)
            return False
        except Exception as e:
            _raise_io_error("Unable to delete attachment file {}.".format(filename), e)
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return True

    #
    def _xpri_get_attach_dir(self) -> str:
        """Return path to attachments work directory, creating it if necessary"""
        attachdir = os.path.join(self._xpri_get_mminsight_scratch_dir(), "attach")
        if not os.path.isdir(attachdir):
            os.mkdir(attachdir)
        return attachdir

    #
    def _xpri_ensure_attach_dir_exists(self) -> None:
        self._xpri_get_attach_dir()

    #
    def _xpri_get_attach_op_id(self) -> int:
        self._last_attach_id = self._last_attach_id + 1
        return self._last_attach_id

    #
    def _xpri_load_attach_tags(self) -> bool:
        if not self._has_fetched_attach_tag_types:
            #
            if self._test_cfile_path != "":
                (attach_tags, default_attach_tags,) = read_attachment_tags_from_cfile(
                    self._test_cfile_path
                )
                self._attach_tags = attach_tags
                self._default_attach_tags = default_attach_tags

                self._has_fetched_attach_tag_types = True
            else:
                #
                self._has_fetched_attach_tag_types = True

        return self._has_fetched_attach_tag_types

    #
    def _xpri_ensure_scen_attach_cache_exists(self, scenario_id: str) -> None:
        """Ensures the scenario attachment cache for the given scenario id exists"""

        if scenario_id not in self._scen_attach_cache_map:
            #
            #
            self._scen_attach_cache_map[scenario_id] = XpriAttachmentsCache(
                type=AttachType.SCENARIO, id=scenario_id, is_populated=False
            )

    #
    def _xpri_get_test_mode_dir(self, attach_cache: XpriAttachmentsCache):
        """
        Return the directory to use to store simulated attachments when in test mode, creating it if it does not exist
        """

        root_dir = self._test_attach_dir
        if root_dir == "":
            root_dir = os.path.join(self._work_dir, self._test_attach_dir)
        if attach_cache.type == AttachType.APP:
            #
            if self._test_mode_app_attach_dir == "":
                test_mode_dir = os.path.join(root_dir, "appattach")
            else:
                test_mode_dir = self._test_mode_app_attach_dir
        elif attach_cache.type == AttachType.SCENARIO:
            if attach_cache.id != self._scenario_id:
                raise NotImplementedError(
                    "Insight test mode currently only supports accessing attachments of current scenario & app."
                )
            if self._test_mode_scen_attach_dir == "":
                test_mode_dir = os.path.join(root_dir, "scenattach")
            else:
                test_mode_dir = self._test_mode_scen_attach_dir
        else:
            raise Exception(
                "Unrecognized attachment cache type: {}.".format(attach_cache.type)
            )

        #
        if not os.path.isdir(test_mode_dir):
            os.makedirs(test_mode_dir)

        return test_mode_dir

    #
    def _xpri_load_attach_rules(self):
        if not self._has_fetched_attach_rules:
            #
            self._attach_rules = AttachmentRules(
                max_size=150 * 1024 * 1024,
                max_attach_count=250,
                max_filename_len=255,
                invalid_filename_chars=list(r'\/?*:|"<>'),
                max_description_len=2500,
            )

    #

    #
    def _xpri_get_test_mode_attachments(
            self, attach_cache: XpriAttachmentsCache
    ) -> Dict[str, XpriAttachment]:
        #
        #
        #
        #
        #

        base = self._xpri_get_test_mode_dir(attach_cache)
        attachments: Dict[str, XpriAttachment] = {}

        for root, _, files in os.walk(base):
            for file in files:
                abs_filename = os.path.join(root, file)
                filename = os.path.relpath(abs_filename, base)
                (_, ext) = os.path.splitext(file)

                if ext not in (".properties", ".properties~"):
                    #
                    props_filename = abs_filename + ".properties"

                    #
                    if os.path.isfile(props_filename):
                        attach: Attachment = read_attach_info(props_filename)

                        #
                        if attach.filename == "" or attach.filename is None:
                            attach.filename = filename

                    else:

                        attach: Attachment = Attachment(
                            filename=filename,
                            description="",
                            tags=[],
                            size=os.path.getsize(abs_filename),
                            last_modified_user="Test User",
                            last_modified_date=datetime.datetime.fromtimestamp(
                                os.path.getmtime(abs_filename)
                            ),
                            hidden=False,
                        )

                        #
                        if attach_cache.type == AttachType.APP:
                            #
                            if not self._xpri_load_attach_tags():
                                raise Exception("Unable to load attach tags.")

                            for (tag, filenames) in self._default_attach_tags.items():
                                if filename in filenames and tag not in attach.tags:
                                    attach.tags.append(tag)

                        #
                        write_attach_info(attach, props_filename)

                    #
                    xpri_attach: XpriAttachment = XpriAttachment(
                        filename=attach.filename,
                        description=attach.description,
                        tags=attach.tags,
                        size=attach.size,
                        last_modified_user=attach.last_modified_user,
                        last_modified_date=attach.last_modified_date,
                        hidden=attach.hidden,
                        local_content_filename=filename,
                    )

                    if file in attachments:
                        _raise_runtime_error(
                            f"Multiple attachments on same item have filename: {xpri_attach.filename}."
                        )
                    else:
                        attachments[xpri_attach.filename] = xpri_attach

        return attachments

    #
    def _xpri_find_test_mode_attachment(
            self, attach_cache: XpriAttachmentsCache, attach_name: str
    ) -> XpriAttachment:

        attachments = self._xpri_get_test_mode_attachments(attach_cache)

        return attachments.get(attach_name, None)

    #
    def _xpri_attach_exists(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> bool:
        #

        assert attach_cache.is_populated

        return self._xpri_find_test_mode_attachment(attach_cache, filename) is not None

    #
    def _xpri_save_test_mode_attachment_properties(
            self, attach_cache: XpriAttachmentsCache, new_props: XpriAttachment
    ) -> None:
        """Save the attachment properties of a given attachment"""

        attach = new_props  #

        props_filename = os.path.join(
            self._xpri_get_test_mode_dir(attach_cache),
            new_props.local_content_filename + ".properties",
        )
        write_attach_info(attach, props_filename, "attach")

    #
    def _xpri_populate_cache(self, attach_cache: XpriAttachmentsCache) -> bool:

        if attach_cache.is_populated:
            return True
        else:
            #
            attach_cache.is_populated = True
            return True

    #
    def _xpri_add_cached_content_changes(
            self, attach_cache: XpriAttachmentsCache, changes_doc: List[Dict]
    ) -> None:
        #

        #
        attach_cache_items = sorted_by_key(attach_cache.attachments)

        for (attachment_filename, att) in attach_cache_items:
            changes_doc.append(
                {
                    "updateType": AttachUpdateType.CREATE.value,
                    "attachmentType": attach_cache.type,
                    "filename": attachment_filename,
                    "contentPath": os.path.join(
                        ATTACH_DIR_RELATIVE_TO_INSTANCE_ROOT, att.local_content_filename
                    ),
                    "size": att.size,
                    "description": att.description,
                    "tags": att.tags,
                    "hidden": att.hidden,
                }
            )

    #
    def _xpri_add_attachment_updates(self, changes_doc: List[Dict]) -> None:
        #

        for upd in self._attachment_updates:

            if upd.update_type == AttachUpdateType.DELETE:
                changes_doc.append(
                    {
                        "updateType": AttachUpdateType.DELETE.value,
                        "attachmentType": upd.attach_type.value,
                        "id": upd.attach_id,
                    }
                )
            elif upd.update_type == AttachUpdateType.FILENAME:
                changes_doc.append(
                    {
                        "updateType": AttachUpdateType.FILENAME.value,
                        "attachmentType": upd.attach_type.value,
                        "id": upd.attach_id,
                        "filename": upd.filename,
                    }
                )
            elif upd.update_type == AttachUpdateType.DESCRIPTION:
                changes_doc.append(
                    {
                        "updateType": AttachUpdateType.DESCRIPTION.value,
                        "attachmentType": upd.attach_type.value,
                        "id": upd.attach_id,
                        "description": upd.description,
                    }
                )
            elif upd.update_type == AttachUpdateType.TAGS:
                changes_doc.append(
                    {
                        "updateType": AttachUpdateType.TAGS.value,
                        "attachmentType": upd.attach_type.value,
                        "id": upd.attach_id,
                        "tags": upd.tags,
                    }
                )
            elif upd.update_type == AttachUpdateType.HIDDEN:
                changes_doc.append(
                    {
                        "updateType": AttachUpdateType.HIDDEN.value,
                        "attachmentType": upd.attach_type.value,
                        "id": upd.attach_id,
                        "hidden": upd.hidden,
                    }
                )
            elif upd.update_type == AttachUpdateType.CONTENT:
                changes_doc.append(
                    {
                        "updateType": AttachUpdateType.CONTENT.value,
                        "attachmentType": upd.attach_type.value,
                        "filename": upd.filename,
                        "contentPath": os.path.join(
                            ATTACH_DIR_RELATIVE_TO_INSTANCE_ROOT,
                            upd.local_content_filename,
                        ),
                        "size": upd.size,
                    }
                )
            else:
                #
                #
                print("ERROR: Unexpected update type: {}.".format(upd.update_type))

    #
    def _xpri_check_can_add_new_attach(
            self, attach_cache: XpriAttachmentsCache
    ) -> bool:
        #

        if attach_cache.type != AttachType.SCENARIO:
            raise NotImplementedError(
                "Attachment rules for attachment type '{}' not implemented.".format(
                    attach_cache.type
                )
            )

        self._xpri_load_attach_rules()
        assert self._attach_rules is not None
        test_attachments = self._xpri_get_test_mode_attachments(attach_cache)
        return len(test_attachments) < self._attach_rules.max_attach_count

    #
    def _xpri_check_attach_filename(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> bool:
        """Check whether an attachment's filename is valid"""

        del attach_cache  #

        self._xpri_load_attach_rules()
        assert self._attach_rules is not None
        if filename == "" or len(filename) > self._attach_rules.max_filename_len:
            return False
        else:
            for c in self._attach_rules.invalid_filename_chars:
                if c in filename:
                    return False

            return True

    #
    def _xpri_check_attach_file_size(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> bool:
        #

        del attach_cache  #

        self._xpri_load_attach_rules()
        assert self._attach_rules is not None
        return os.path.getsize(filename) <= self._attach_rules.max_size

    #
    def _xpri_check_attach_description(
            self, attach_cache: XpriAttachmentsCache, description: str
    ) -> bool:
        """Check whether an attachment's description is valid"""

        del attach_cache  #

        self._xpri_load_attach_rules()
        assert self._attach_rules is not None
        return len(description) <= self._attach_rules.max_description_len

    #
    def _xpri_check_tags_valid(self, tags: List[str]) -> bool:
        #
        if not self._xpri_load_attach_tags():
            return False  #
        else:
            for t in tags:
                if t not in self._attach_tags:
                    return False

            return True

    #
    def _xpri_get_attach_common(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> AttachStatus:
        #

        #
        if not self._xpri_populate_cache(attach_cache):
            return AttachStatus.RUNTIME_ERROR

        else:
            #
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                return AttachStatus.NOT_FOUND
            else:
                src = os.path.join(
                    self._xpri_get_test_mode_dir(attach_cache),
                    test_attach.local_content_filename,
                )
                try:
                    shutil.copy(src, filename)
                except Exception as e:
                    _raise_io_error(f"Unable to write or overwrite file {filename}.", e)
                    return AttachStatus.RUNTIME_ERROR

                return AttachStatus.OK

    #
    def _xpri_get_attach(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> None:
        status = self._xpri_get_attach_common(attach_cache, filename)
        self._xpri_attach_stat = status

    #
    def _xpri_remove_attach_updates(
            self, attach_id: str, attach_type: AttachType, update_type: AttachUpdateType
    ) -> None:
        #
        self._attachment_updates = [
            u
            for u in self._attachment_updates
            if u.attach_id != attach_id
            or u.update_type != update_type
            or u.attach_type != attach_type
        ]

    #
    def _xpri_put_attach(
            self, attach_cache: XpriAttachmentsCache, filename: str, overwrite: bool
    ) -> None:
        #

        self._xpri_clear_attach_stat()

        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return

        #
        if not overwrite and self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.ALREADY_EXISTS)
            return

        if not self._xpri_check_attach_filename(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.INVALID_FILENAME)
            return

        if not self._xpri_check_can_add_new_attach(
                attach_cache
        ) and not self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.TOO_MANY)
            return

        #
        if not os.path.isfile(filename):
            _raise_io_error("Attachment file '{}' not found.".format(filename))
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return

        if not self._xpri_check_attach_file_size(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.TOO_LARGE)
            return

        #
        test_attach: XpriAttachment = self._xpri_find_test_mode_attachment(
            attach_cache, filename
        )
        if test_attach is None:
            #
            test_attach = XpriAttachment(
                filename=filename,
                description="",
                tags=[],
                hidden=False,
                local_content_filename=filename,
            )

            c = 1
            while os.path.isfile(
                    os.path.join(
                        self._xpri_get_test_mode_dir(attach_cache),
                        test_attach.local_content_filename,
                    )
            ):
                c = c + 1
                test_attach.local_content_filename = "{}_{}".format(filename, c)

        #
        test_attach.size = os.path.getsize(filename)
        test_attach.last_modified_user = self.username
        test_attach.last_modified_date = datetime.datetime.now()

        #
        test_attach_path = os.path.join(
            self._xpri_get_test_mode_dir(attach_cache),
            test_attach.local_content_filename,
        )

        try:
            os.makedirs(os.path.dirname(test_attach_path), exist_ok=True)
        except Exception as e:
            _raise_io_error(f"Unable to create parent directory for file {test_attach_path}.", e)
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return

        try:
            shutil.copy(filename, test_attach_path)
        except Exception as e:
            _raise_io_error(f"Unable to copy attachment from {filename} to {test_attach_path}.", e)
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return

        #
        #
        if self._xpri_attach_stat == AttachStatus.IN_PROGRESS:
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)
            self._xpri_set_attach_stat(AttachStatus.OK)

    #
    def _xpri_delete_attach(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> None:
        #
        runtime_error = False

        self._xpri_clear_attach_stat()

        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)

        #
        elif not self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)

        else:
            att: XpriAttachment = self._xpri_find_test_mode_attachment(
                attach_cache, filename
            )
            if att is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            att_path = os.path.join(
                self._xpri_get_test_mode_dir(attach_cache), att.local_content_filename
            )

            try:
                os.remove(att_path)
            except Exception as e:
                _raise_io_error("Unable to delete attachment file {}.".format(att_path), e)
                self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
                runtime_error = True

            if not runtime_error:
                prop_file = att_path + ".properties"
                if os.path.isfile(prop_file):
                    try:
                        os.remove(prop_file)
                    except Exception as e:
                        _raise_io_error("Unable to delete attachment file {}.".format(prop_file), e)
                        self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
                        runtime_error = True

            if not runtime_error:
                self._xpri_set_attach_stat(AttachStatus.OK)

    #
    #
    def _xpri_rename_attach(
            self, attach_cache: XpriAttachmentsCache, old_name: str, new_name: str
    ) -> None:

        self._xpri_clear_attach_stat()
        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)

        #
        elif old_name == new_name:
            #
            self._xpri_set_attach_stat(AttachStatus.OK)
        elif not self._xpri_attach_exists(attach_cache, old_name):
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)
        elif self._xpri_attach_exists(attach_cache, new_name):
            self._xpri_set_attach_stat(AttachStatus.ALREADY_EXISTS)
        elif not self._xpri_check_attach_filename(attach_cache, new_name):
            self._xpri_set_attach_stat(AttachStatus.INVALID_FILENAME)

        #
        else:
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, old_name)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            test_attach.filename = new_name
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)
            self._xpri_set_attach_stat(AttachStatus.OK)

    #
    #
    def _xpri_set_attach_desc(
            self, attach_cache: XpriAttachmentsCache, filename: str, description: str
    ):

        self._xpri_clear_attach_stat()
        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)

        #
        elif not self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)
        elif not self._xpri_check_attach_description(attach_cache, description):
            self._xpri_set_attach_stat(AttachStatus.INVALID_DESCRIPTION)

        #
        else:
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            test_attach.description = description
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)
            self._xpri_set_attach_stat(AttachStatus.OK)

    #
    #
    def _xpri_set_attach_tags(
            self, attach_cache: XpriAttachmentsCache, filename: str, new_tags: List[str]
    ):
        #
        #
        #
        #
        #

        self._xpri_clear_attach_stat()
        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)

        #
        elif not self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)

        #
        elif not self._xpri_check_tags_valid(new_tags):
            self._xpri_set_attach_stat(AttachStatus.INVALID_TAGS)

        #
        else:
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            test_attach.tags = list(set(new_tags))  #
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)

            #
            all_test_attach = None
            for tag in new_tags:
                if self._attach_tags[tag].usage == AttachTagUsage.SINGLE_FILE:
                    if all_test_attach is None:
                        all_test_attach = self._xpri_get_test_mode_attachments(
                            attach_cache
                        )

                    for (test_attach_filename, attachment) in all_test_attach.items():
                        if test_attach_filename != filename and tag in attachment.tags:
                            self._xpri_save_test_mode_attachment_properties(
                                attach_cache, attachment
                            )

            self._xpri_set_attach_stat(AttachStatus.OK)

    #
    #
    def _xpri_set_attach_hidden(
            self, attach_cache: XpriAttachmentsCache, filename: str, hidden: bool
    ) -> None:

        self._xpri_clear_attach_stat()
        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)

        #
        elif not self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)

        #
        else:
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")
            test_attach.hidden = hidden
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)
            self._xpri_set_attach_stat(AttachStatus.OK)

    #
    def _xpri_list_attach_common(
            self, attach_cache: XpriAttachmentsCache
    ) -> Tuple[AttachStatus, Optional[List[Attachment]]]:
        #

        #
        if not self._xpri_populate_cache(attach_cache):
            return (AttachStatus.RUNTIME_ERROR, None)

        else:
            test_attachments = self._xpri_get_test_mode_attachments(attach_cache)
            sorted_test_attachments = sorted_by_key(test_attachments)
            return (AttachStatus.OK, sorted_test_attachments)

    #
    def _xpri_list_attach(self, attach_cache: XpriAttachmentsCache) -> List[Attachment]:
        #

        self._xpri_clear_attach_stat()
        (status, attachments) = self._xpri_list_attach_common(attach_cache)
        self._xpri_set_attach_stat(status)
        if status == AttachStatus.OK:
            assert attachments is not None
            return attachments
        else:
            return []

    #
    #
    def _xpri_list_attach_by_tag_common(
            self, attach_cache: XpriAttachmentsCache, tag: str
    ) -> Tuple[AttachStatus, Optional[List[Attachment]]]:
        (status, all_attachments) = self._xpri_list_attach_common(attach_cache)
        if status != AttachStatus.OK:
            return (status, None)
        else:
            assert all_attachments is not None
            attachments = [attach for attach in all_attachments if tag in attach.tags]
            return (AttachStatus.OK, attachments)

    #
    #
    def _xpri_list_attach_by_tag(
            self, attach_cache: XpriAttachmentsCache, tag: str
    ) -> List[Attachment]:
        self._xpri_clear_attach_stat()
        if not self._xpri_check_tags_valid([tag]):
            self._xpri_set_attach_stat(AttachStatus.INVALID_TAGS)
            return []
        else:
            (status, attachments) = self._xpri_list_attach_by_tag_common(
                attach_cache, tag
            )
            self._xpri_set_attach_stat(status)
            return attachments

    #
    #
    def _xpri_get_attach_info(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> Optional[Attachment]:

        self._xpri_clear_attach_stat()

        #
        if not self._xpri_populate_cache(attach_cache):
            self._xpri_set_attach_stat(AttachStatus.RUNTIME_ERROR)
            return None
        elif not self._xpri_attach_exists(attach_cache, filename):
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)
            return None
        else:
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")
            attach = copy.deepcopy(test_attach)
            self._xpri_set_attach_stat(AttachStatus.OK)
            return attach

    #
    #
    def _xpri_get_scenario_id(self, scenario_path: str) -> str:
        if scenario_path == self._scenario_path:
            return self._scenario_id
        else:
            raise NotImplementedError("Access to other scenarios is currently not supported in Insight test mode.")

    #
    #
    def _xpri_get_attachs_by_tag(self, tag: str) -> Optional[List[Attachment]]:
        self._xpri_clear_attach_stat()

        #
        if not self._xpri_check_tags_valid([tag]):
            self._xpri_set_attach_stat(AttachStatus.INVALID_TAGS)
            return None

        #
        attach_cache = self._scen_attach_cache_map[self._scenario_id]
        (status, a) = self._xpri_list_attach_by_tag_common(attach_cache, tag)

        #
        if status != AttachStatus.OK:
            self._xpri_set_attach_stat(status)
            return None

        #
        if a == []:
            attach_cache = self._app_attach_cache
            (status, a) = self._xpri_list_attach_by_tag_common(attach_cache, tag)
            if status != AttachStatus.OK:
                self._xpri_set_attach_stat(status)
                return None

        #
        if a == []:
            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)
            return None

        #
        assert a is not None
        for attach in a:
            status = self._xpri_get_attach_common(attach_cache, attach.filename)
            if status != AttachStatus.OK:
                break

        #
        self._xpri_set_attach_stat(status)
        return a

    #
    #
    def _xpri_get_attach_filenames_by_tag(self, tag: str) -> List[str]:
        attachments = self._xpri_get_attachs_by_tag(tag)
        if self._xpri_attach_stat == AttachStatus.OK:
            assert attachments is not None
            return [attach.filename for attach in attachments]
        else:
            return []

    #
    #
    def _xpri_get_attach_by_tag(self, tag: str) -> Optional[Attachment]:
        self._xpri_clear_attach_stat()
        if not self._xpri_check_tags_valid([tag]):
            self._xpri_set_attach_stat(AttachStatus.INVALID_TAGS)
            return None
        else:
            (status, a) = self._xpri_list_attach_by_tag_common(
                self._scen_attach_cache_map[self._scenario_id], tag
            )
            if status != AttachStatus.OK:
                self._xpri_set_attach_stat(status)
                return None
            else:
                assert a is not None
                if len(a) > 1:
                    self._xpri_set_attach_stat(AttachStatus.SEVERAL_FOUND)
                    return None
                elif len(a) == 1:
                    attachment = a[0]
                    status = self._xpri_get_attach_common(
                        self._scen_attach_cache_map[self._scenario_id],
                        attachment.filename,
                    )
                    self._xpri_set_attach_stat(status)  #
                    return attachment
                else:
                    (status, a) = self._xpri_list_attach_by_tag_common(
                        self._app_attach_cache, tag
                    )
                    if status != AttachStatus.OK:
                        self._xpri_set_attach_stat(status)
                        return None
                    else:
                        assert a is not None
                        if len(a) == 0:
                            self._xpri_set_attach_stat(AttachStatus.NOT_FOUND)
                            return None
                        elif len(a) > 1:
                            self._xpri_set_attach_stat(AttachStatus.SEVERAL_FOUND)
                            return None
                        else:
                            attachment = a[0]
                            status = self._xpri_get_attach_common(
                                self._app_attach_cache, attachment.filename
                            )
                            self._xpri_set_attach_stat(
                                status
                            )  #
                            return attachment

    #

    #

    @property
    def scenario_id(self):
        return self._scenario_id

    @scenario_id.setter
    def scenario_id(self, scenario_id: str):
        self._scenario_id = scenario_id

    @property
    def scenario_name(self) -> str:
        return self._scenario_name

    @scenario_name.setter
    def scenario_name(self, scenario_name: str):
        self._scenario_name = scenario_name

    @property
    def scenario_path(self) -> str:
        return self._scenario_path

    @scenario_path.setter
    def scenario_path(self, scenario_path: str):
        path = RepositoryPath(scenario_path)

        if not path.is_absolute:
            raise ValueError("The scenario path must be absolute.")

        #
        path = path.abspath(current_dir=RepositoryPath('/'))

        if len(path.elements) <= 1:
            raise ValueError("The normalized scenario path must have more than one elements. "
                             "Example: '/appname/scenname'")

        self._scenario_path = str(path)

    def update(self, metric: Metric, value: Union[float, int, ObjSense]) -> None:
        pass

    def reset_progress(self) -> None:
        pass
