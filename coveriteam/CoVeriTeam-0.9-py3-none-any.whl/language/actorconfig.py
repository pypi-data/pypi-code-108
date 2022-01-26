# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import yaml
import benchexec
from pathlib import Path
from coveriteam.util import (
    is_url,
    download_if_needed,
    unzip,
    get_ARCHIVE_DOWNLOAD_PATH,
)
import coveriteam.util as util
import re
from coveriteam.language import CoVeriLangException
import os
import requests
import json


class ActorDefinitionLoader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = Path(stream.name).parent
        super(ActorDefinitionLoader, self).__init__(stream)

    def include(self, node):
        filename = self._root / self.construct_scalar(node)
        with filename.open("r") as f:
            d = yaml.load(f, ActorDefinitionLoader)  # noqa S506
            return dict_merge(d, {"imported_file": filename})

    @staticmethod
    def load_config(path):
        with open(path, "r") as f:
            try:
                d = yaml.load(f, ActorDefinitionLoader)  # noqa S506
            except yaml.YAMLError as e:
                msg = "Actor config yaml file {} is invalid: {}".format(path, e)
                raise CoVeriLangException(msg, 203)

            return d

    @staticmethod
    def resolve_includes(d):
        # Check if "imports" exist
        imports = d.pop("imports", None)
        if not imports:
            return d

        if not isinstance(imports, list):
            imports = [imports]

        di = {}
        for i in imports:
            i.pop("imported_file", None)
            di = dict_merge(di, ActorDefinitionLoader.resolve_includes(i))
        return dict_merge(di, d)

    @staticmethod
    def collect_included_files(d):
        f = d.pop("imported_file", None)
        f = [] if f is None else [str(f)]
        # Check if "imports" exist
        imports = d.pop("imports", None)
        if not imports:
            return f

        if not isinstance(imports, list):
            imports = [imports]

        fs = []
        for i in imports:
            fs += ActorDefinitionLoader.collect_included_files(i)
        return fs + f


class ActorConfig:
    def __init__(self, path, version=None):

        ActorDefinitionLoader.add_constructor("!include", ActorDefinitionLoader.include)
        self.path = path
        self.get_actor_config()

        if self._config["format_version"] != "1.2":
            raise CoVeriLangException(
                f"Actor {path} version is not version 1.2 "
                + f"but version {self._config['format_version']}",
                200,
            )

        self.actor_name = self._config["actor_name"]
        self.reslim = self._config["resourcelimits"]

        # We take the first available version in case of None or an empty string.
        if not version:
            logging.warn(
                f"Warning: No version specified for actor {self.actor_name}. Taking the first version from the actor definition file.\n"
                + "You can specify the tool's version as a third parameter in the call to ActorFactory.create()."
            )

            if len(self._config["archives"]) <= 0:
                raise CoVeriLangException(
                    f"{self.actor_name} doesn't have any versions specified!"
                )
            self.version = str(self._config["archives"][0]["version"])
        else:
            self.version = str(version)

        tool_configs = [
            x for x in self._config["archives"] if str(x["version"]) == self.version
        ]
        if len(tool_configs) > 1:
            raise CoVeriLangException(
                "There a multiple versions in the yaml file with the same name!", 2
            )

        tool_config = tool_configs[0]
        if tool_config is None:
            raise CoVeriLangException(
                f'{self.actor_name} doesn\'t recognize the requested version "{self.version}"!'
            )

        assert ("location" in tool_config) != ("doi" in tool_config)

        if "options" in tool_config:
            self.options = tool_config["options"]
        else:
            logging.debug("No options override found, hence using global options.")
            self.options = self._config["options"]

        if "doi" in tool_config:
            doi = tool_config["doi"]
            check_allowed_doi(doi)
            if util.UPDATE_CACHE:
                self.archive_location = get_archive_url_from_zenodo_doi(doi)
                self.archive_name = self.get_archive_name()
            self.tool_dir = str(util.get_INSTALL_DIR() / doi.replace("/", "-"))
        else:
            self.archive_location = tool_config["location"]
            check_policy_compliance(self)
            self.archive_name = self.get_archive_name()
            # Keeping this path as str instead of Path because it is going to be used with string paths mostly.
            self.tool_dir = self.get_tool_installation_dir()

        if util.UPDATE_CACHE:
            self.__install_if_needed()
        self.__resolve_tool_info_module()

    def get_archive_name(self):
        archive_name = self.archive_location.rpartition("/")[2]
        if archive_name.endswith(".zip"):
            archive_name = archive_name.rpartition(".")[0]
        archive_name += "-" + self.version + ".zip"
        return archive_name

    def get_tool_installation_dir(self):
        # I think it is easier for debugging if the dir name starts with the archive name.
        # So, we take out the archive name and put it in the front instead of at the end.
        url_root = self.archive_location.rpartition("/")[0]
        if self.archive_name.endswith(".zip"):
            archive_name = self.archive_name.rpartition(".")[0]
        tool_dir_name = (
            archive_name + "-" + url_root.replace("://", "-").replace("/", "-")
        )
        return str(util.get_INSTALL_DIR() / tool_dir_name)

    def get_actor_config(self):
        self._config = ActorDefinitionLoader.load_config(self.path)
        self._config = ActorDefinitionLoader.resolve_includes(self._config)
        self.__check_actor_definition_integrity()
        self.__sanitize_yaml_dict()

    def __check_actor_definition_integrity(self):
        # check if the essential tags are present.
        # Essentiality of tags can be defined in a schema.
        essential_tags = [
            "toolinfo_module",
            "resourcelimits",
            "actor_name",
            "archives",
            "format_version",
        ]
        diff = essential_tags - self._config.keys()
        if diff:
            msg = (
                "The following tags are missing in the actor config YAML: "
                + self.path
                + "\n"
                + "\n".join(diff)
            )
            raise CoVeriLangException(msg, 200)

    def __sanitize_yaml_dict(self):
        # translate resource limits
        reslim = self._config.get("resourcelimits", None)
        if reslim:
            if reslim.get("memlimit"):
                reslim["memlimit"] = benchexec.util.parse_memory_value(
                    reslim.get("memlimit")
                )
            if reslim.get("timelimit"):
                reslim["timelimit"] = benchexec.util.parse_timespan_value(
                    reslim.get("timelimit")
                )
            self._config["resourcelimits"] = reslim

    def __install_if_needed(self):
        target_dir = Path(self.tool_dir)

        if not re.compile("^[A-Za-z0-9-._]+$").match(self.archive_name):
            raise CoVeriLangException(
                "Can't download tool because the version name contains invalid characters!",
                200,
            )

        archive_download_path = get_ARCHIVE_DOWNLOAD_PATH() / self.archive_name
        downloaded = download_if_needed(self.archive_location, archive_download_path)

        # Unzip only if downloaded or the tool directory does not exist.
        if downloaded or not target_dir.is_dir():
            print("Installing the actor: " + self.actor_name + "......")
            unzip(archive_download_path, target_dir)

    def __resolve_tool_info_module(self):
        """
        1. Check if it is a URL.
        2. If a URL then download it and save it to the TI cache.
        3. Infer the module name and return it.
        """
        # TODO the extraction of the tool info module name should be separated from downloading.
        ti = self._config["toolinfo_module"]
        if is_url(ti):
            filename = util.get_TOOL_INFO_DOWNLOAD_PATH() / ti.rpartition("/")[2]
            if util.UPDATE_CACHE:
                download_if_needed(ti, filename)
            ti = "." + filename.name

        if ti.endswith(".py"):
            ti = ti.rpartition(".")[0]

        self.tool_name = ti


def dict_merge(d1, d2):
    # This function recursively merges (updates) the dictionaries.
    for k in d2.keys():
        if k in d1.keys() and isinstance(d1[k], dict) and isinstance(d2[k], dict):
            if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                d1[k] = dict_merge(d1[k], d2[k])
            elif isinstance(d1[k], dict) or isinstance(d2[k], dict):
                # TODO this could be and XOR
                # We raise an error when one of the values is a dict, but not the other.
                msg = "YAML file could not be parsed. Clash in the tag: %r" % k
                raise CoVeriLangException(msg, 201)
            else:
                d1[k] = d2[k]
        else:
            d1[k] = d2[k]

    return d1


def load_policy(policy_file):
    if not policy_file:
        if os.getenv("COVERITEAM_POLICY"):
            policy_file = os.getenv("COVERITEAM_POLICY")
        else:
            return {}

    with open(policy_file, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            msg = "Failed to load policy from: {} Error is: {}".format(policy_file, e)
            raise CoVeriLangException(msg, 202)


def check_policy_compliance_allowed_locations(allowed_locations, archive_location):
    # Expression to match nothing.
    e = "a^"
    for loc in allowed_locations:
        e = "%s|(%s)" % (e, re.escape(loc))
    if not re.compile(e).match(archive_location):
        msg = "Not allowed to download from the url: %s" % archive_location
        raise CoVeriLangException(msg, 100)


def check_policy_compliance(ac, policy_file=None):
    policy = load_policy(policy_file)
    allowed_locations = policy.get("allowed_locations", None)
    if allowed_locations:
        check_policy_compliance_allowed_locations(
            allowed_locations, ac.archive_location
        )


def check_allowed_doi(doi):
    parts = doi.rsplit("/")
    if len(parts) != 2:
        raise CoVeriLangException("Strange DOI! This DOI is not allowed.")

    if parts[0] != "10.5281" or parts[1].rsplit(".")[0] != "zenodo":
        raise CoVeriLangException(
            "This DOI is not allowed. Only Zenodo DOIs are allowed."
        )


def get_archive_url_from_zenodo_doi(doi):
    ZENODO_API_URL_BASE = "https://zenodo.org/api/records/"
    zenodo_record_id = doi.rsplit(".")[-1]
    url = ZENODO_API_URL_BASE + zenodo_record_id
    response = requests.get(url)
    data = json.loads(response.content)
    if len(data["files"]) > 1:
        raise CoVeriLangException(
            "More than one files are linked in this Zenodo record. The record should have only one file."
        )
    archive_url = data["files"][0]["links"]["self"]
    return archive_url
