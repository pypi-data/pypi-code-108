import asyncio
from logging import getLogger
from typing import List, Optional, cast, TypeVar, Type, Tuple

import urllib3

from rallycli import BaseAPI
from rallycli.errors import RallyError
from rallycli.models import type_names, RallyTypeGeneric, Artifact, US
## logger definition
from rallycli.models.artifact_models import Feature, Defect, SchedulabeArtifact

logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()

T = TypeVar('T')


class ArtifactAPI(BaseAPI):
    """
    Class for Artifact abstract model management and specific functions for subclasses:
    - US
    - Defect
    - Feature
    - ...
    """

    def get_artifact_by_formattedid(self, formattedid: str) -> Optional[T]:
        art_type_name: str
        art_type_name, art_class = self._get_type_from_formattedid(formattedid)
        result_lst: List[RallyTypeGeneric] = self.query(f"(FormattedID = {formattedid})",
                                                        art_type_name,
                                                        model_class=art_class)
        art_class: Type[T] = art_class
        if result_lst:
            return cast(art_class.__name__, result_lst[0])
        else:
            return None

    def get_flowstates_for_project(self, project_ref: str, fetch: str = "true",
                                   order_by: str = "OrderIndex") -> List[RallyTypeGeneric]:
        flows: List[RallyTypeGeneric] = self.query(f"(Project = {project_ref})",
                                                   type_names.FLOWSTATE,
                                                   fetch=fetch,
                                                   order_by=order_by)
        return flows

    def get_typedef_states(self, type_name: str) -> List[RallyTypeGeneric]:
        params = {
            "query": f"(TypeDef.Name = \"{type_name}\")",
            "fetch": "Name"
        }
        return self._simple_query(params, type_names.STATE, [])

    def create_artifact(self, art_model: T, art_type: str) -> T:
        self._check_artifact_type(art_model)
        result_object: dict = self._create_from_model(art_model.copy_for_create(), rally_type=art_type)
        obj = self._get_rally_object(result_object, model_class=art_model.__class__)
        return obj

    def update_artifact(self, art_model: T, art_type: str, body_keys: List[str] = None) -> T:
        self._check_artifact_type(art_model)
        key_set: set = set(body_keys) if body_keys else set()
        result_object: dict = self._update_from_model(art_model.copy_for_update(body_keys=key_set), rally_type=art_type)
        obj = self._get_rally_object(result_object, art_model.__class__)
        return obj

    def update_artifact_list(self,
                             art_models: List[T],
                             art_type: str,
                             body_keys: List[str] = None) -> Optional[List[T]]:
        self._check_artifact_type(art_models[0])
        key_set: set = set(body_keys) if body_keys else set()
        url_data: List[Tuple[str, dict]] = []
        for art in art_models:
            url: str = f"{art._ref}{BaseAPI._security_key}"
            data: dict = {art_type: art.copy_for_update(body_keys=key_set)}
            url_data.append((url, data))

        result_objects: List[dict] = asyncio.run(self._async_post_elements(url_data))
        objs: List[T] = [self._get_rally_object(robj, art_models[0].__class__) for robj in result_objects]
        return objs

    def delete_artifact(self, art_model: T):
        self._check_artifact_type(art_model)
        art_model.clean_for_update()
        return self._delete_from_model(art_model)

    def add_refs_to_artifact_attribute_collection(self, artifact: Artifact, refs: List[str],collection_name: str):

        self._add_members_refs_to_collection(artifact._ref, refs, collection_name)


    def delete_refs_from_artifact_attribute_collection(self, artifact: Artifact, refs: List[str], collection_name: str):

        self._delete_members_refs_from_collection(artifact._ref, refs, collection_name)


    ## Feature

    def add_tags_to_artifact(self, artifact: Artifact, tags: List[RallyTypeGeneric]):
        cs_refs = [cs._ref for cs in tags]
        self._add_members_refs_to_collection(artifact._ref, cs_refs, "tags")

    def add_changesets_to_artifact(self, artifact: Artifact, changesets: List[RallyTypeGeneric]):
        cs_refs = [cs._ref for cs in changesets]
        self._add_members_refs_to_collection(artifact._ref, cs_refs, "changesets")

    def add_userstories_to_feature(self, feature: Artifact, userstories: List[US]):
        us_refs = [u._ref for u in userstories]
        self._add_members_refs_to_collection(feature._ref, us_refs, "userstories")

    def set_portfolioitems_state_by_name(self, portfolioitems: List[Artifact], target_state_name: str, type_name: str):
        """Set state for a list of portfolio items of one specific typedef"""
        states: List[RallyTypeGeneric] = self.get_typedef_states(type_name)
        target_state_lst = list(filter(lambda s: s.Name == target_state_name, states))
        if not target_state_lst:
            raise RallyError(f"No State found for typedef: {type_name} with name: {target_state_name}")
        target_state = target_state_lst[0]
        for item in portfolioitems:
            item.State = target_state._ref
            self.update_artifact(item, type_name, ["State"])

    def set_artifacts_schedulestate(self, artifacts: List[SchedulabeArtifact], target_state_name: str, type_name: str):
        """Set state for a list of portfolio items of one specific typedef"""
        if target_state_name not in type_names.SCHEDULESTATE.keys():
            raise RallyError(f"'{target_state_name}' is not a valid schedulestate. Valid list: "
                             f"\n {type_names.SCHEDULESTATE.keys()}")
        for item in artifacts:
            item.ScheduleState = target_state_name
            self.update_artifact(item, type_name, ["ScheduleState"])

    @staticmethod
    def _check_artifact_type(art_model):
        # Artifacts subdomains must extend Artifact class
        if not isinstance(art_model, Artifact):
            raise ValueError(f"'{type(art_model)}' is not a valid Artifact type")

    @staticmethod
    def _get_type_from_formattedid(formattedid: str) -> Tuple[str, Type]:
        """
        Parameters
        ----------
        formattedid: Rally Artifact FormattedID like FE2343 or US34234

        Returns
        -------
        Tuple <rally_type_string>,<model_class_for_type>
        """

        if formattedid.startswith("US"):
            return type_names.US, US
        elif formattedid.startswith("DE"):
            return type_names.DEFECT, Defect
        elif formattedid.startswith("TC"):
            return type_names.TESTCASE, RallyTypeGeneric
        elif formattedid.startswith("TS"):
            return type_names.TESTSET, RallyTypeGeneric
        elif formattedid.startswith("TA"):
            return type_names.TASK, RallyTypeGeneric
        elif formattedid.startswith("FE"):
            return type_names.FEATURE, Feature
        elif formattedid.startswith("I"):
            return type_names.INITIATIVE, RallyTypeGeneric
#
