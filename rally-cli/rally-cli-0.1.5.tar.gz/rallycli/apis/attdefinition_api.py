import os
import sys
from logging import getLogger
from typing import List, Optional

import urllib3

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rallycli.base_api import BaseAPI
from rallycli.models import type_names, Attdefinition, AllowedValue, RallyTypeGeneric
from rallycli.utils.orig_utils import get_oid_from_ref

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class AttdefinitionAPI(BaseAPI):
    """Class for accessing AttributeDefinition and AllowedValues domain"""

    ## AttributeDefinition

    def get_attribute_by_name(self, typedef_ref: str, att_name: str, fetch: str = "true") -> Optional[Attdefinition]:
        typedef_oid = get_oid_from_ref(typedef_ref)
        type_name = f"{type_names.TYPEDEF}/{typedef_oid}/attributes"
        params = dict(self._baseparams, query=f"( Name = \"{att_name}\" )")
        result: List[Attdefinition] = self._simple_query(params=params,
                                                         rally_type=type_name,
                                                         keys=[],
                                                         model_class=Attdefinition)
        if result:
            return result[0]
        else:
            return None

    def create_attribute(self, attribute: Attdefinition) -> Attdefinition:
        created: dict = self._create_from_model(attribute, rally_type=type_names.ATTDEFINITION)
        return Attdefinition(**created)

    def update_attribute(self, attribute: Attdefinition, body_keys: List[str] = None) -> Attdefinition:
        logger.debug(attribute)
        key_set: set = set(body_keys) if body_keys else set()
        return Attdefinition(**self._update_from_model(attribute.copy_for_update(key_set), type_names.ATTDEFINITION))

    ## AllowedAttributeDefinitionValue

    def add_new_attribute_allowed_values(self, attribute: Attdefinition, allowedvaluelist: List[AllowedValue]):
        for value in allowedvaluelist:
            value.AttributeDefinition = attribute._ref
            self._create_from_model(value.copy_for_create(), type_names.ALLOWEDVALUE)

    def delete_attribute_allowed_values(self, allowedvaluelist: List[AllowedValue]):
        for value in allowedvaluelist:
            self._delete_from_model(value)

    def get_allowed_values_from_att(self, attribute: Attdefinition, fetch: str = "true") -> List[AllowedValue]:
        return self.get_elements_by_ref(elements_ref=attribute.AllowedValues._ref,
                                        fetch=fetch,
                                        pagesize=2000,
                                        model_class=AllowedValue)

    def update_allowed_value(self, allowed_value: AllowedValue, keys: List[str] = None) -> AllowedValue:
        keyset = set(keys) if keys else None
        updated: dict = self._update_from_model(allowed_value.copy_for_update(body_keys=keyset), type_names.ALLOWEDVALUE)
        return AllowedValue(**updated)

    ## Scoped Attributes

    def set_attribute_project_visibility(self,
                                         project_ref: str,
                                         typedef_ref: str,
                                         attribute_ref: str,
                                         att_visible: bool) -> RallyTypeGeneric:
        ## .../Project/66370034821/TypeDefinition/66370034965/ScopedAttributeDefinition/67310617601
        typedef_oid = get_oid_from_ref(typedef_ref)
        att_oid = get_oid_from_ref(attribute_ref)
        url = f"{project_ref}/TypeDefinition/{typedef_oid}/ScopedAttributeDefinition/{att_oid}"
        data = {
            "ScopedAttributeDefinition": {
                "Hidden": not att_visible
            }
        }
        return RallyTypeGeneric(**self._post(url, data))
