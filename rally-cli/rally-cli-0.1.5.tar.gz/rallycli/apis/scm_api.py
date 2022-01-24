import os
import sys
from datetime import datetime
from logging import getLogger
from typing import List, Optional

import urllib3

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rallycli.base_api import BaseAPI
from rallycli.models import type_names, RallyTypeGeneric

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class ScmAPI(BaseAPI):
    """Class for accessing SCM & Build domain"""
    BUILD_SUCCESS = "SUCCESS"
    BUILD_FAILURE = "FAILURE"
    BUILD_INCOMPLETE = "INCOMPLETE"
    BUILD_UNKNOWN = "UNKNOWN"
    BUILD_NO_BUILDS = "NO BUILDS"

    ## Pull Request

    def get_pullrequests_for_project(self, project_ref: str, fetch: str = "true") -> List[RallyTypeGeneric]:
        return self.query(f"(Project = {project_ref})", type_names.PULLREQUEST, fetch=fetch)

    ## Changeset

    def get_scmrepo_by_name(self, name: str) -> Optional[RallyTypeGeneric]:
        result = self.query(f"( Name = {name})", type_names.SCMREPO)
        if result:
            return result[0]
        else:
            return None

    def create_scmrepo(self, name: str, scm_type: str, url: str, project_ref: str = None) -> RallyTypeGeneric:
        scm_repo: RallyTypeGeneric = RallyTypeGeneric(**{"Name": name, "SCMType": scm_type, "Url": url})
        created_scm_repo: RallyTypeGeneric = RallyTypeGeneric(**self._create_from_model(scm_repo, type_names.SCMREPO))
        if created_scm_repo and project_ref:
            self._add_members_refs_to_collection(parent_ref=created_scm_repo._ref, collection_refs=[project_ref],
                                                 collection_name="projects")
        return created_scm_repo

    def create_changeset(self, scm_repo_ref: str, author_ref: str, branch: str,
                         commit_ts: datetime, revision: str, uri: str) -> RallyTypeGeneric:
        changeset: RallyTypeGeneric = RallyTypeGeneric(**{"Branch": branch, "CommitTimestamp": commit_ts,
                                                          "Revision": revision, "Uri": uri})
        changeset.SCMRepository = {"_ref": scm_repo_ref}
        changeset.Author = {"_ref": author_ref}
        return RallyTypeGeneric(**self._create_from_model(changeset, type_names.CHANGESET))

    ## Pull Request

    def create_pullrequest(self, project_ref: str, artifact_ref: str,
                           external_formatted_id: str,
                           external_id: str,
                           name: str,
                           description: str,
                           url: str):
        pullrequest: RallyTypeGeneric = RallyTypeGeneric(**{"ExternalFormattedID": external_formatted_id,
                                                            "ExternalID": external_id,
                                                            "Name": name,
                                                            "Description": description,
                                                            "Url": url})
        pullrequest.Project = {"_ref": project_ref}
        pullrequest.Artifact = {"_ref": artifact_ref}
        return RallyTypeGeneric(**self._create_from_model(pullrequest, type_names.PULLREQUEST))

    ## Build

    def get_build_definition_by_name(self, name: str) -> Optional[RallyTypeGeneric]:
        result = self.query(f"( Name = {name})", type_names.BUILDDEFINITION)
        if result:
            return result[0]
        else:
            return None

    def create_build_definition(self, project_ref: str, name: str, description, url: str) -> RallyTypeGeneric:
        build_def: RallyTypeGeneric = RallyTypeGeneric(**{"name": name, "url": url, "description": description})
        build_def.Project = {"_ref": project_ref}
        return RallyTypeGeneric(**self._create_from_model(build_def, type_names.BUILDDEFINITION))

    def create_build(self, build_def_ref: str, build_number_label: str,
                     status: str, duration: float, url: str,
                     change_sets: List[RallyTypeGeneric] = None) -> RallyTypeGeneric:
        build: RallyTypeGeneric = RallyTypeGeneric(**{"Duration": duration, "Number": build_number_label, "Url": url})
        build.BuildDefinition = {"_ref": build_def_ref}
        # Supported Statuses "SUCCESS", "FAILURE", "INCOMPLETE", "UNKNOWN", "NO BUILDS"
        build.Status = status
        if change_sets:
            build.Changesets = change_sets
        return RallyTypeGeneric(**self._create_from_model(build, type_names.BUILD))
