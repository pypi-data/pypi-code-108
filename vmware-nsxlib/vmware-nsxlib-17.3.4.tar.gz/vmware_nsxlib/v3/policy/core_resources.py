# Copyright 2017 VMware, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import abc
from distutils import version
import sys

import decorator
import eventlet
from oslo_log import log as logging
from oslo_utils import uuidutils

from vmware_nsxlib._i18n import _
from vmware_nsxlib.v3 import exceptions
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3 import utils

from vmware_nsxlib.v3.policy import constants
from vmware_nsxlib.v3.policy import core_defs
from vmware_nsxlib.v3.policy import transaction as trans
from vmware_nsxlib.v3.policy import utils as p_utils

LOG = logging.getLogger(__name__)

# Sentitel object to indicate unspecified attribute value
# None value in attribute would indicate "unset" functionality,
# while "ignore" means that the value not be present in request
# body
IGNORE = object()

DEFAULT_MAP_ID = 'DEFAULT'


@decorator.decorator
def check_allowed_passthrough(f, *args, **kwargs):
    resource_api = args[0]
    if not resource_api.nsx_api:
        caller = sys._getframe(1).f_code.co_name
        LOG.error("%s failed: Passthrough api is disabled", caller)
        return

    return f(*args, **kwargs)


class NsxPolicyResourceBase(object, metaclass=abc.ABCMeta):
    """Abstract class for NSX policy resources

    declaring the basic apis each policy resource should support,
    and implement some common apis and utilities
    """
    SINGLE_ENTRY_ID = 'entry'

    def __init__(self, policy_api, nsx_api, version, nsxlib_config):
        self.policy_api = policy_api
        self.nsx_api = nsx_api
        self.version = version
        self.nsxlib_config = nsxlib_config

    @property
    def entry_def(self):
        pass

    @abc.abstractmethod
    def list(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get(self, uuid, *args, **kwargs):
        pass

    @abc.abstractmethod
    def delete(self, uuid, *args, **kwargs):
        pass

    @abc.abstractmethod
    def create_or_overwrite(self, *args, **kwargs):
        """Create new or overwrite existing resource

           Create would list keys and attributes, set defaults and
           perform necessary validations.
           If object with same IDs exists on backend, it will
           be overridden.
        """
        pass

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """Update existing resource

           Update is different from create since it specifies only
           attributes that need changing. Non-updateble attributes
           should not be listed as update arguments.
           Create_or_overwrite is not
           good enough since it sets defaults, and thus would return
           non-default values to default if not specified in kwargs.
        """
        pass

    def _any_arg_set(self, *args):
        """Helper to identify if user specified any of args"""
        for arg in args:
            if arg != IGNORE:
                return True

        return False

    def _get_user_args(self, **kwargs):
        return {key: value for key, value in kwargs.items()
                if value != IGNORE}

    def _init_def(self, **kwargs):
        """Helper for update function - ignore attrs without explicit value"""
        args = self._get_user_args(**kwargs)
        return self.entry_def(nsx_version=self.version, **args)

    def _init_parent_def(self, **kwargs):
        """Helper for update function - ignore attrs without explicit value"""
        args = self._get_user_args(**kwargs)
        return self.parent_entry_def(**args)

    def _get_and_update_def(self, **kwargs):
        """Helper for update function - ignore attrs without explicit value"""
        args = self._get_user_args(**kwargs)
        resource_def = self.entry_def(nsx_version=self.version, **args)
        body = self.policy_api.get(resource_def)
        if body:
            resource_def.set_obj_dict(body)

        return resource_def

    def _update(self, allow_partial_updates=True,
                force=False, put=False, revision=None, **kwargs):
        """Helper for update function - ignore attrs without explicit value"""
        # DO NOT retry if caller specifies revision
        max_attempts = (self.policy_api.client.max_attempts
                        if revision is None else 0)

        @utils.retry_upon_exception(
            exceptions.StaleRevision,
            max_attempts=max_attempts)
        def _do_update_with_retry():
            if (allow_partial_updates and
                    self.policy_api.partial_updates_supported() and not put):
                policy_def = self._init_def(**kwargs)
                partial_updates = True
            else:
                policy_def = self._get_and_update_def(**kwargs)
                partial_updates = False

            if policy_def.bodyless():
                # Nothing to update - only keys provided in kwargs
                return
            if put:
                return self.policy_api.update_with_put(
                    policy_def, revision=revision)
            else:
                self.policy_api.create_or_update(
                    policy_def, partial_updates=partial_updates, force=force)

        return _do_update_with_retry()

    @staticmethod
    def _init_obj_uuid(obj_uuid):
        if not obj_uuid:
            # generate a random id
            obj_uuid = str(uuidutils.generate_uuid())
        return obj_uuid

    def _canonize_name(self, name):
        # remove spaces and slashes from objects names
        return name.replace(' ', '_').replace('/', '_')

    def get_by_name(self, name, *args, **kwargs):
        # Return first match by name
        resources_list = self.list(*args, **kwargs)
        for obj in resources_list:
            if obj.get('display_name') == name:
                return obj

    def _get_realization_info(self, resource_def, entity_type=None,
                              silent=False, all_results=False):
        entities = []
        results = []
        try:
            path = resource_def.get_resource_full_path()
            entities = self.policy_api.get_realized_entities(
                path, silent=silent)
            if entities:
                if entity_type:
                    # look for the entry with the right entity_type
                    for entity in entities:
                        if entity.get('entity_type') == entity_type:
                            if all_results:
                                results.append(entity)
                            else:
                                return entity
                    return results
                else:
                    # return the first realization entry
                    # (Useful for resources with single realization entity)
                    if not all_results:
                        return entities[0]
                    else:
                        return entities
        except exceptions.ResourceNotFound:
            pass

        # If we got here the resource was not deployed yet
        if silent:
            LOG.debug("No realization info found for %(path)s type %(type)s: "
                      "%(entities)s",
                      {"path": path, "type": entity_type,
                       "entities": entities})
        else:
            LOG.warning("No realization info found for %(path)s type %(type)s",
                        {"path": path, "type": entity_type})

    def _get_realized_state(self, resource_def, entity_type=None,
                            realization_info=None):
        if not realization_info:
            realization_info = self._get_realization_info(
                resource_def, entity_type=entity_type)
        if realization_info and realization_info.get('state'):
            return realization_info['state']

    def _get_realized_id(self, resource_def, entity_type=None,
                         realization_info=None):
        if not realization_info:
            realization_info = self._get_realization_info(
                resource_def, entity_type=entity_type)
        if (realization_info and
            realization_info.get('realization_specific_identifier')):
            return realization_info['realization_specific_identifier']

    def _get_realization_error_message_and_code(self, info):
        error_msg = 'unknown'
        error_code = None
        related_error_codes = []
        if info.get('alarms'):
            alarm = info['alarms'][0]
            error_msg = alarm.get('message')
            if alarm.get('error_details'):
                error_code = alarm['error_details'].get('error_code')
                if alarm['error_details'].get('related_errors'):
                    related = alarm['error_details']['related_errors']
                    for err_obj in related:
                        error_msg = '%s: %s' % (error_msg,
                                                err_obj.get('error_message'))
                        if err_obj.get('error_code'):
                            related_error_codes.append(err_obj['error_code'])
        return error_msg, error_code, related_error_codes

    def _wait_until_realized(self, resource_def, entity_type=None,
                             sleep=None, max_attempts=None,
                             all_results=False):
        """Wait until the resource has been realized

        Return the realization info, or raise an error
        """
        if sleep is None:
            sleep = self.nsxlib_config.realization_wait_sec
        if max_attempts is None:
            max_attempts = self.nsxlib_config.realization_max_attempts
        info = {}

        @utils.retry_upon_none_result(max_attempts, delay=sleep, random=True)
        def get_info():
            info = self._get_realization_info(
                resource_def, entity_type=entity_type,
                silent=True, all_results=all_results)
            error_entity = None
            if info:
                # the state can be 'REALIZED'/'UNREALIZED'/'ERROR'
                if isinstance(info, list):
                    # check all the realization entry
                    i = 0
                    for entity in info:
                        if entity['state'] == constants.STATE_REALIZED:
                            i += 1
                            continue
                        if entity['state'] == constants.STATE_ERROR:
                            error_entity = entity
                            break
                    # all the entities are in "REALIZED" state
                    if i == len(info):
                        # return all the realization entities
                        return info
                else:
                    if info['state'] == constants.STATE_REALIZED:
                        return info
                    if info['state'] == constants.STATE_ERROR:
                        error_entity = info
                if error_entity:
                    error_msg, error_code, related_error_codes = \
                        self._get_realization_error_message_and_code(
                            error_entity)
                    # There could be a delay between setting NSX-T
                    # Error realization state and updating the realization
                    # entity with alarms. Retry should be perform upon None
                    # error code to avoid 'Unknown' RealizationErrorStateError
                    # exception
                    if error_code is None:
                        return
                    raise exceptions.RealizationErrorStateError(
                        resource_type=resource_def.resource_type(),
                        resource_id=resource_def.get_id(),
                        error=error_msg, error_code=error_code,
                        related_error_codes=related_error_codes)

        try:
            return get_info()
        except exceptions.RealizationError as e:
            raise e
        except Exception:
            # max retries reached
            LOG.error("_wait_until_realized maxed-out for "
                      "resource: %s. Last realization info was %s",
                      resource_def.get_resource_full_path(), info)

            raise exceptions.RealizationTimeoutError(
                resource_type=resource_def.resource_type(),
                resource_id=resource_def.get_id(),
                attempts=max_attempts,
                sleep=sleep)

    def _wait_until_state_successful(self, res_def,
                                     sleep=None, max_attempts=None,
                                     with_refresh=False):
        res_path = res_def.get_resource_full_path()
        state = {}
        if sleep is None:
            sleep = self.nsxlib_config.realization_wait_sec
        if max_attempts is None:
            max_attempts = self.nsxlib_config.realization_max_attempts

        @utils.retry_upon_none_result(max_attempts, delay=sleep, random=True)
        def get_state():
            state = self.policy_api.get_intent_consolidated_status(
                res_path, silent=True)
            if state and state.get('consolidated_status'):
                con_state = state['consolidated_status'].get(
                    'consolidated_status')
                if con_state == 'SUCCESS':
                    return True
                if con_state == 'ERROR':
                    LOG.error("_wait_until_state_successful errored for "
                              "resource: %s. Last consolidated_status result "
                              "was %s", res_path, state)
                    raise exceptions.RealizationErrorStateError(
                        resource_type=res_def.resource_type(),
                        resource_id=res_def.get_id(),
                        error="Unknown")
            if with_refresh:
                # Refresh the consolidated state for the next time
                # (if not, it will be refreshed at the policy level after a
                # refresh cycle)
                self.policy_api.refresh_realized_state(res_path)

        try:
            return get_state()
        except exceptions.RealizationError as e:
            raise e
        except Exception:
            # max retries reached
            LOG.error("_wait_until_state_successful maxed-out for "
                      "resource: %s. Last consolidated_status result was %s",
                      res_path, state)

            raise exceptions.RealizationTimeoutError(
                resource_type=res_def.resource_type(),
                resource_id=res_def.get_id(),
                attempts=max_attempts,
                sleep=sleep)

    @check_allowed_passthrough
    def _get_realized_id_using_search(self, policy_resource_path,
                                      mp_resource_type, resource_def=None,
                                      entity_type=None, silent=False,
                                      sleep=None, max_attempts=None):
        """Wait until the policy path will be found using search api

        And return the NSX ID of the MP resource that was found
        """
        if sleep is None:
            sleep = self.nsxlib_config.realization_wait_sec
        if max_attempts is None:
            max_attempts = self.nsxlib_config.realization_max_attempts
        check_status = 3

        tag = [{'scope': 'policyPath',
                'tag': utils.escape_tag_data(policy_resource_path)}]
        resources = []
        test_num = 0
        while test_num < max_attempts:
            # Use the search api to find the realization id of this entity.
            resources = self.nsx_api.search_by_tags(
                tags=tag, resource_type=mp_resource_type,
                silent=silent)['results']
            if resources:
                # If status exists, make sure the state is successful
                if (not resources[0].get('status') or
                    resources[0]['status'].get('state') == 'success'):
                    return resources[0]['id']

            # From time to time also check the Policy realization state,
            # as if it is in ERROR waiting should be avoided.
            if resource_def and test_num % check_status == (check_status - 1):
                info = self._get_realization_info(resource_def,
                                                  entity_type=entity_type)
                if info and info['state'] == constants.STATE_ERROR:
                    error_msg, error_code, related_error_codes = \
                        self._get_realization_error_message_and_code(info)
                    LOG.error("_get_realized_id_using_search Failed for "
                              "resource: %s. Got error in realization info %s",
                              policy_resource_path, info)
                    raise exceptions.RealizationErrorStateError(
                        resource_type=resource_def.resource_type(),
                        resource_id=resource_def.get_id(),
                        error=error_msg, error_code=error_code,
                        related_error_codes=related_error_codes)
                if (info and info['state'] == constants.STATE_REALIZED and
                    info.get('realization_specific_identifier')):
                    LOG.warning("Realization ID for %s was not found via "
                                "search api although it was realized",
                                policy_resource_path)
                    return info['realization_specific_identifier']
            eventlet.sleep(sleep)
            test_num += 1

        # max retries reached
        LOG.error("_get_realized_id_using_search maxed-out for "
                  "resource: %s. Last search result was %s",
                  policy_resource_path, resources)

        raise exceptions.RealizationTimeoutError(
            resource_type=mp_resource_type,
            resource_id=policy_resource_path,
            attempts=max_attempts,
            sleep=sleep)

    def _get_extended_attr_from_realized_info(self, realization_info,
                                              requested_attr):
        # Returns a list. In case a single value is expected,
        # caller must extract the first index to retrieve the value
        if realization_info:
            try:
                for attr in realization_info.get('extended_attributes', []):
                    if attr.get('key') == requested_attr:
                        return attr.get('values')
            except IndexError:
                return

    def _list(self, obj_def, silent=False):
        return self.policy_api.list(obj_def, silent=silent).get('results', [])

    def _create_or_store(self, policy_def, child_def=None):
        transaction = trans.NsxPolicyTransaction.get_current()
        if transaction:
            # Store this def for batch apply for this transaction
            transaction.store_def(policy_def, self.policy_api.client)
            if child_def and not policy_def.mandatory_child_def:
                transaction.store_def(child_def, self.policy_api.client)
        else:
            # No transaction - apply now
            # In case the same object was just deleted, or depends on another
            # resource, create may need to be retried.
            @utils.retry_upon_exception(
                (exceptions.NsxPendingDelete, exceptions.StaleRevision),
                max_attempts=self.policy_api.client.max_attempts)
            def _do_create_with_retry():
                if child_def:
                    self.policy_api.create_with_parent(policy_def, child_def)
                else:
                    self.policy_api.create_or_update(policy_def)

            _do_create_with_retry()

    def _delete_or_store(self, policy_def):
        transaction = trans.NsxPolicyTransaction.get_current()
        if transaction:
            # Mark this resource is about to be deleted
            policy_def.set_delete()
            # Set some mandatory default values to avoid failure
            # TODO(asarfaty): This can be removed once platform bug is fixed
            policy_def.set_default_mandatory_vals()
            # Store this def for batch apply for this transaction
            transaction.store_def(policy_def, self.policy_api.client)
        else:
            # No transaction - apply now
            self._delete_with_retry(policy_def)

    def _delete_with_retry(self, policy_def):

        @utils.retry_upon_exception(
            exceptions.StaleRevision,
            max_attempts=self.policy_api.client.max_attempts)
        def do_delete():
            self.policy_api.delete(policy_def)

        do_delete()


class NsxPolicyDomainApi(NsxPolicyResourceBase):
    """NSX Policy Domain."""
    @property
    def entry_def(self):
        return core_defs.DomainDef

    def create_or_overwrite(self, name, domain_id=None,
                            description=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        domain_id = self._init_obj_uuid(domain_id)
        domain_def = self._init_def(domain_id=domain_id,
                                    name=name,
                                    description=description,
                                    tags=tags,
                                    tenant=tenant)

        self._create_or_store(domain_def)
        return domain_id

    def delete(self, domain_id, tenant=constants.POLICY_INFRA_TENANT):
        domain_def = core_defs.DomainDef(domain_id=domain_id, tenant=tenant)
        self._delete_with_retry(domain_def)

    def get(self, domain_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        domain_def = core_defs.DomainDef(domain_id=domain_id, tenant=tenant)
        return self.policy_api.get(domain_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        domain_def = core_defs.DomainDef(tenant=tenant)
        return self._list(domain_def)

    def update(self, domain_id, name=IGNORE,
               description=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(domain_id=domain_id,
                     name=name,
                     description=description,
                     tags=tags,
                     tenant=tenant)


class NsxPolicyGroupApi(NsxPolicyResourceBase):
    """NSX Policy Group (under a Domain) with condition/s"""
    @property
    def entry_def(self):
        return core_defs.GroupDef

    def create_or_overwrite(
        self, name, domain_id, group_id=None,
        description=IGNORE,
        cond_val=None,
        cond_key=constants.CONDITION_KEY_TAG,
        cond_op=constants.CONDITION_OP_EQUALS,
        cond_member_type=constants.CONDITION_MEMBER_PORT,
        tags=IGNORE,
        tenant=constants.POLICY_INFRA_TENANT):
        """Create a group with/without a condition.

        Empty condition value will result a group with no condition.
        """

        group_id = self._init_obj_uuid(group_id)
        # Prepare the condition
        if cond_val is not None:
            condition = core_defs.Condition(value=cond_val,
                                            key=cond_key,
                                            operator=cond_op,
                                            member_type=cond_member_type)
            conditions = [condition]
        else:
            conditions = []
        group_def = self._init_def(domain_id=domain_id,
                                   group_id=group_id,
                                   name=name,
                                   description=description,
                                   conditions=conditions,
                                   tags=tags,
                                   tenant=tenant)
        self._create_or_store(group_def)
        return group_id

    def build_condition(
        self, cond_val=None,
        cond_key=constants.CONDITION_KEY_TAG,
        cond_op=constants.CONDITION_OP_EQUALS,
        cond_member_type=constants.CONDITION_MEMBER_PORT):
        return core_defs.Condition(value=cond_val,
                                   key=cond_key,
                                   operator=cond_op,
                                   member_type=cond_member_type)

    def build_ip_address_expression(self, ip_addresses):
        return core_defs.IPAddressExpression(ip_addresses)

    def build_path_expression(self, paths):
        return core_defs.PathExpression(paths)

    def build_union_condition(self, operator=constants.CONDITION_OP_OR,
                              conditions=None):
        # NSX don't allow duplicate expressions in expression list
        # of a group -> (ERROR: Duplicate expressions specified)
        # Members of input conditions is either instance of Condition
        # or NestedExpression class.
        expressions = []
        if conditions:
            conditions = list(set(conditions))
            expressions = []
            for cond in conditions:
                if len(expressions):
                    expressions.append(core_defs.ConjunctionOperator(
                        operator=operator))
                expressions.append(cond)
        return expressions

    def build_nested_condition(
        self, operator=constants.CONDITION_OP_AND,
        conditions=None):
        expressions = self.build_union_condition(
            operator=operator, conditions=conditions)
        return core_defs.NestedExpression(expressions=expressions)

    def create_or_overwrite_with_conditions(
        self, name, domain_id, group_id=None,
        description=IGNORE,
        conditions=IGNORE, tags=IGNORE,
        tenant=constants.POLICY_INFRA_TENANT):
        """Create a group with a list of conditions.

        To build the conditions in the list, build_condition
        or build_nested_condition can be used
        """
        group_id = self._init_obj_uuid(group_id)
        if not conditions:
            conditions = []
        group_def = self._init_def(domain_id=domain_id,
                                   group_id=group_id,
                                   name=name,
                                   description=description,
                                   conditions=conditions,
                                   tags=tags,
                                   tenant=tenant)
        self._create_or_store(group_def)
        return group_id

    def delete(self, domain_id, group_id,
               tenant=constants.POLICY_INFRA_TENANT):
        group_def = core_defs.GroupDef(domain_id=domain_id,
                                       group_id=group_id,
                                       tenant=tenant)
        self._delete_with_retry(group_def)

    def get(self, domain_id, group_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        group_def = core_defs.GroupDef(domain_id=domain_id,
                                       group_id=group_id,
                                       tenant=tenant)
        return self.policy_api.get(group_def, silent=silent)

    def list(self, domain_id,
             tenant=constants.POLICY_INFRA_TENANT):
        """List all the groups of a specific domain."""
        group_def = core_defs.GroupDef(domain_id=domain_id,
                                       tenant=tenant)
        return self._list(group_def)

    def get_by_name(self, domain_id, name,
                    tenant=constants.POLICY_INFRA_TENANT):
        """Return first group matched by name of this domain"""
        return super(NsxPolicyGroupApi, self).get_by_name(name, domain_id,
                                                          tenant=tenant)

    def update(self, domain_id, group_id,
               name=IGNORE, description=IGNORE,
               tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT):
        self._update(domain_id=domain_id,
                     group_id=group_id,
                     name=name,
                     description=description,
                     tags=tags,
                     tenant=tenant)

    def update_with_conditions(
        self, domain_id, group_id,
        name=IGNORE, description=IGNORE, conditions=IGNORE,
        tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT,
        update_payload_cbk=None):
        group_def = self._init_def(domain_id=domain_id,
                                   group_id=group_id,
                                   name=name,
                                   description=description,
                                   conditions=conditions,
                                   tags=tags,
                                   tenant=tenant)
        group_path = group_def.get_resource_path()

        @utils.retry_upon_exception(
            exceptions.StaleRevision,
            max_attempts=self.policy_api.client.max_attempts)
        def _update():
            # Get the current data of group
            group = self.policy_api.get(group_def)
            if update_payload_cbk:
                # The update_payload_cbk function takes two arguments.
                # The first one is the result from the internal GET request.
                # The second one is a dict of user-provided attributes,
                # which can be changed inside the callback function and
                # used as the new payload for the following PUT request.
                # For example, users want to combine the new conditions
                # passed to update_with_conditions() with the original
                # conditions retrieved from the internal GET request
                # instead of overriding the original conditions.
                update_payload_cbk(group, group_def.attrs)
            group_def.set_obj_dict(group)
            body = group_def.get_obj_dict()
            # Update the entire group at the NSX
            self.policy_api.client.update(group_path, body)

        _update()

    def get_realized_state(self, domain_id, group_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        group_def = core_defs.GroupDef(domain_id=domain_id,
                                       group_id=group_id,
                                       tenant=tenant)
        return self._get_realized_state(group_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, domain_id, group_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        group_def = core_defs.GroupDef(domain_id=domain_id,
                                       group_id=group_id,
                                       tenant=tenant)
        return self._get_realized_id(group_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, domain_id, group_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        group_def = core_defs.GroupDef(domain_id=domain_id,
                                       group_id=group_id,
                                       tenant=tenant)
        return self._get_realization_info(group_def, entity_type=entity_type,
                                          silent=silent)

    def get_path(self, domain_id, group_id,
                 tenant=constants.POLICY_INFRA_TENANT):
        group_def = self.entry_def(domain_id=domain_id,
                                   group_id=group_id,
                                   tenant=tenant)
        return group_def.get_resource_full_path()

    def wait_until_realized(self, domain_id, group_id,
                            entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        group_def = self.entry_def(domain_id=domain_id, group_id=group_id,
                                   tenant=tenant)
        return self._wait_until_realized(group_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)


class NsxPolicyServiceBase(NsxPolicyResourceBase):
    """Base class for NSX Policy Service with a single entry.

    Note the nsx-policy backend supports multiple service entries per service.
    At this point this is not supported here.
    """

    @property
    def parent_entry_def(self):
        return core_defs.ServiceDef

    def delete(self, service_id,
               tenant=constants.POLICY_INFRA_TENANT):
        """Delete the service with all its entries"""
        service_def = core_defs.ServiceDef(service_id=service_id,
                                           tenant=tenant)
        self._delete_with_retry(service_def)

    def get(self, service_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        service_def = core_defs.ServiceDef(service_id=service_id,
                                           tenant=tenant)
        return self.policy_api.get(service_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        service_def = core_defs.ServiceDef(tenant=tenant)
        return self._list(service_def)

    def get_realized_state(self, service_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        service_def = core_defs.ServiceDef(service_id=service_id,
                                           tenant=tenant)
        return self._get_realized_state(service_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, service_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        service_def = core_defs.ServiceDef(service_id=service_id,
                                           tenant=tenant)
        return self._get_realized_id(service_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, service_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        service_def = core_defs.ServiceDef(service_id=service_id,
                                           tenant=tenant)
        return self._get_realization_info(service_def,
                                          entity_type=entity_type,
                                          silent=silent)


class NsxPolicyL4ServiceApi(NsxPolicyServiceBase):
    """NSX Policy Service with a single L4 service entry.

    Note the nsx-policy backend supports multiple service entries per service.
    At this point this is not supported here.
    """

    @property
    def entry_def(self):
        return core_defs.L4ServiceEntryDef

    def create_or_overwrite(self, name, service_id=None,
                            description=IGNORE,
                            protocol=constants.TCP,
                            dest_ports=IGNORE,
                            source_ports=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        service_id = self._init_obj_uuid(service_id)
        service_def = self._init_parent_def(service_id=service_id,
                                            name=name,
                                            description=description,
                                            tags=tags,
                                            tenant=tenant)
        entry_def = self._init_def(service_id=service_id,
                                   entry_id=self.SINGLE_ENTRY_ID,
                                   name=self.SINGLE_ENTRY_ID,
                                   protocol=protocol,
                                   dest_ports=dest_ports,
                                   source_ports=source_ports,
                                   tenant=tenant)

        service_def.mandatory_child_def = entry_def
        self._create_or_store(service_def, entry_def)
        return service_id

    def update(self, service_id,
               name=IGNORE, description=IGNORE,
               protocol=IGNORE, dest_ports=IGNORE, source_ports=IGNORE,
               tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT):

        parent_def = self._init_parent_def(
            service_id=service_id,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant)

        entry_def = self._get_and_update_def(
            service_id=service_id,
            entry_id=self.SINGLE_ENTRY_ID,
            protocol=protocol,
            dest_ports=dest_ports,
            source_ports=source_ports,
            tenant=tenant)

        self.policy_api.create_with_parent(parent_def, entry_def)

    def build_entry(self, name, service_id, entry_id,
                    description=None, protocol=None,
                    dest_ports=None, source_ports=None,
                    tags=None, tenant=constants.POLICY_INFRA_TENANT):
        return self._init_def(service_id=service_id,
                              entry_id=entry_id,
                              name=name,
                              description=description,
                              protocol=protocol,
                              dest_ports=dest_ports,
                              source_ports=source_ports,
                              tags=tags,
                              tenant=tenant)


class NsxPolicyIcmpServiceApi(NsxPolicyServiceBase):
    """NSX Policy Service with a single ICMP service entry.

    Note the nsx-policy backend supports multiple service entries per service.
    At this point this is not supported here.
    """
    @property
    def entry_def(self):
        return core_defs.IcmpServiceEntryDef

    def create_or_overwrite(self, name, service_id=None,
                            description=IGNORE,
                            version=4, icmp_type=IGNORE, icmp_code=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        service_id = self._init_obj_uuid(service_id)
        service_def = self._init_parent_def(service_id=service_id,
                                            name=name,
                                            description=description,
                                            tags=tags,
                                            tenant=tenant)
        entry_def = self._init_def(
            service_id=service_id,
            entry_id=self.SINGLE_ENTRY_ID,
            name=self.SINGLE_ENTRY_ID,
            version=version,
            icmp_type=icmp_type,
            icmp_code=icmp_code,
            tenant=tenant)

        service_def.mandatory_child_def = entry_def
        self._create_or_store(service_def, entry_def)
        return service_id

    def update(self, service_id,
               name=IGNORE, description=IGNORE,
               version=IGNORE, icmp_type=IGNORE,
               icmp_code=IGNORE, tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        parent_def = self._init_parent_def(
            service_id=service_id,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant)

        entry_def = self._get_and_update_def(
            service_id=service_id,
            entry_id=self.SINGLE_ENTRY_ID,
            version=version,
            icmp_type=icmp_type,
            icmp_code=icmp_code,
            tenant=tenant)

        return self.policy_api.create_with_parent(parent_def, entry_def)

    def build_entry(self, name, service_id, entry_id,
                    description=None, version=4,
                    icmp_type=None, icmp_code=None,
                    tags=None, tenant=constants.POLICY_INFRA_TENANT):
        return self._init_def(service_id=service_id,
                              entry_id=entry_id,
                              name=name,
                              description=description,
                              version=version,
                              icmp_type=icmp_type,
                              icmp_code=icmp_code,
                              tags=tags,
                              tenant=tenant)


class NsxPolicyIPProtocolServiceApi(NsxPolicyServiceBase):
    """NSX Policy Service with a single IPProtocol service entry.

    Note the nsx-policy backend supports multiple service entries per service.
    At this point this is not supported here.
    """
    @property
    def entry_def(self):
        return core_defs.IPProtocolServiceEntryDef

    def create_or_overwrite(self, name, service_id=None,
                            description=IGNORE,
                            protocol_number=IGNORE, tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        service_id = self._init_obj_uuid(service_id)
        service_def = self._init_parent_def(service_id=service_id,
                                            name=name,
                                            description=description,
                                            tags=tags,
                                            tenant=tenant)
        entry_def = self._init_def(
            service_id=service_id,
            entry_id=self.SINGLE_ENTRY_ID,
            name=self.SINGLE_ENTRY_ID,
            protocol_number=protocol_number,
            tenant=tenant)

        service_def.mandatory_child_def = entry_def
        self._create_or_store(service_def, entry_def)
        return service_id

    def update(self, service_id,
               name=IGNORE, description=IGNORE,
               protocol_number=IGNORE, tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        parent_def = self._init_parent_def(
            service_id=service_id,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant)

        entry_def = self._get_and_update_def(
            service_id=service_id,
            entry_id=self.SINGLE_ENTRY_ID,
            protocol_number=protocol_number,
            tenant=tenant)

        return self.policy_api.create_with_parent(parent_def, entry_def)

    def build_entry(self, name, service_id, entry_id,
                    description=None, protocol_number=None,
                    tags=None, tenant=constants.POLICY_INFRA_TENANT):
        return self._init_def(service_id=service_id,
                              entry_id=entry_id,
                              name=name,
                              protocol_number=protocol_number,
                              tags=tags,
                              tenant=tenant)


class NsxPolicyMixedServiceApi(NsxPolicyServiceBase):
    """NSX Policy Service with mixed service entries."""

    def create_or_overwrite(self, name, service_id,
                            description=IGNORE,
                            entries=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        service_def = self._init_parent_def(service_id=service_id,
                                            name=name,
                                            description=description,
                                            entries=entries,
                                            tags=tags,
                                            tenant=tenant)

        if entries != IGNORE:
            self._create_or_store(service_def, entries)
        else:
            self._create_or_store(service_def)
        return service_id

    def update(self, service_id,
               name=IGNORE, description=IGNORE,
               entries=IGNORE, tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        parent_def = self._init_parent_def(
            service_id=service_id,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant)

        if entries != IGNORE:
            self.policy_api.create_with_parent(parent_def, entries)
        else:
            self.policy_api.create_or_update(parent_def)


class NsxPolicyTier1Api(NsxPolicyResourceBase):
    """NSX Tier1 API """
    LOCALE_SERVICE_SUFF = '-0'

    @property
    def entry_def(self):
        return core_defs.Tier1Def

    def build_route_advertisement(self, static_routes=False, subnets=False,
                                  nat=False, lb_vip=False, lb_snat=False,
                                  ipsec_endpoints=False):
        return core_defs.RouteAdvertisement(static_routes=static_routes,
                                            subnets=subnets,
                                            nat=nat,
                                            lb_vip=lb_vip,
                                            lb_snat=lb_snat,
                                            ipsec_endpoints=ipsec_endpoints)

    def create_or_overwrite(self, name, tier1_id=None,
                            description=IGNORE,
                            tier0=IGNORE,
                            force_whitelisting=IGNORE,
                            failover_mode=constants.NON_PREEMPTIVE,
                            route_advertisement=IGNORE,
                            dhcp_config=IGNORE,
                            disable_firewall=IGNORE,
                            ipv6_ndra_profile_id=IGNORE,
                            pool_allocation=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        tier1_id = self._init_obj_uuid(tier1_id)
        tier1_def = self._init_def(tier1_id=tier1_id,
                                   name=name,
                                   description=description,
                                   tier0=tier0,
                                   force_whitelisting=force_whitelisting,
                                   tags=tags,
                                   failover_mode=failover_mode,
                                   route_advertisement=route_advertisement,
                                   dhcp_config=dhcp_config,
                                   disable_firewall=disable_firewall,
                                   ipv6_ndra_profile_id=ipv6_ndra_profile_id,
                                   pool_allocation=pool_allocation,
                                   tenant=tenant)

        self._create_or_store(tier1_def)
        return tier1_id

    def delete(self, tier1_id, tenant=constants.POLICY_INFRA_TENANT):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        self._delete_with_retry(tier1_def)

    def get(self, tier1_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        return self.policy_api.get(tier1_def, silent=silent)

    def get_path(self, tier1_id, tenant=constants.POLICY_INFRA_TENANT):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        return tier1_def.get_resource_full_path()

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        tier1_def = self.entry_def(tenant=tenant)
        return self._list(tier1_def)

    def update(self, tier1_id, name=IGNORE, description=IGNORE,
               force_whitelisting=IGNORE,
               failover_mode=IGNORE, tier0=IGNORE,
               dhcp_config=IGNORE, tags=IGNORE,
               enable_standby_relocation=IGNORE,
               disable_firewall=IGNORE,
               ipv6_ndra_profile_id=IGNORE,
               route_advertisement=IGNORE,
               route_advertisement_rules=IGNORE,
               pool_allocation=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT,
               current_body=None):

        self._update(tier1_id=tier1_id,
                     name=name,
                     description=description,
                     force_whitelisting=force_whitelisting,
                     failover_mode=failover_mode,
                     dhcp_config=dhcp_config,
                     tier0=tier0,
                     enable_standby_relocation=enable_standby_relocation,
                     disable_firewall=disable_firewall,
                     ipv6_ndra_profile_id=ipv6_ndra_profile_id,
                     route_advertisement=route_advertisement,
                     route_advertisement_rules=route_advertisement_rules,
                     pool_allocation=pool_allocation,
                     tags=tags,
                     tenant=tenant)

    def update_route_advertisement(
        self, tier1_id,
        static_routes=None,
        subnets=None,
        nat=None,
        lb_vip=None,
        lb_snat=None,
        ipsec_endpoints=None,
        tier0=IGNORE,
        tenant=constants.POLICY_INFRA_TENANT):

        tier1_dict = self.get(tier1_id, tenant)
        route_adv = self.entry_def.get_route_adv(tier1_dict)
        route_adv.update(static_routes=static_routes,
                         subnets=subnets,
                         nat=nat,
                         lb_vip=lb_vip,
                         lb_snat=lb_snat,
                         ipsec_endpoints=ipsec_endpoints)

        self.update(tier1_id,
                    route_advertisement=route_adv,
                    tier0=tier0,
                    tenant=tenant)

    def add_advertisement_rule(
            self, tier1_id, name, action=None, prefix_operator=None,
            route_advertisement_types=None, subnets=None,
            tenant=constants.POLICY_INFRA_TENANT):
        tier1_dict = self.get(tier1_id, tenant)
        adv_rules = tier1_dict.get('route_advertisement_rules', [])
        adv_rules = [r for r in adv_rules if r.get('name') != name]

        adv_rule = core_defs.RouteAdvertisementRule(
            name=name, action=action, prefix_operator=prefix_operator,
            route_advertisement_types=route_advertisement_types,
            subnets=subnets)
        adv_rules.append(adv_rule)
        self.update(tier1_id,
                    route_advertisement_rules=adv_rules,
                    tenant=tenant,
                    current_body=tier1_dict)

    def remove_advertisement_rule(self, tier1_id, name,
                                  tenant=constants.POLICY_INFRA_TENANT):
        tier1_dict = self.get(tier1_id, tenant)
        adv_rules = tier1_dict.get('route_advertisement_rules', [])
        updated_adv_rules = [r for r in adv_rules if r.get('name') != name]
        if updated_adv_rules != adv_rules:
            self.update(tier1_id,
                        route_advertisement_rules=updated_adv_rules,
                        tenant=tenant,
                        current_body=tier1_dict)

    def build_advertisement_rule(self, name, action=None, prefix_operator=None,
                                 route_advertisement_types=None, subnets=None):
        return core_defs.RouteAdvertisementRule(
            name=name, action=action, prefix_operator=prefix_operator,
            route_advertisement_types=route_advertisement_types,
            subnets=subnets)

    def update_advertisement_rules(self, tier1_id, rules=None,
                                   name_prefix=None,
                                   tenant=constants.POLICY_INFRA_TENANT):
        """Update the router advertisement rules

        If name_prefix is None, replace the entire list of NSX rules with the
        new given 'rules'.
        Else - delete the NSX rules with this name prefix, and add 'rules' to
        the rest.
        """
        tier1_dict = self.get(tier1_id, tenant)
        current_rules = tier1_dict.get('route_advertisement_rules', [])
        if name_prefix:
            # delete rules with this prefix:
            new_rules = []
            for rule in current_rules:
                if (not rule.get('name') or
                    not rule['name'].startswith(name_prefix)):
                    new_rules.append(rule)
            # add new rules if provided
            if rules:
                new_rules.extend(rules)
        else:
            new_rules = rules

        self.update(tier1_id,
                    route_advertisement_rules=new_rules,
                    tenant=tenant,
                    current_body=tier1_dict)

    @staticmethod
    def _locale_service_id(tier1_id):
        # Supporting only a single locale-service per router for now
        # with the same id as the router id with a constant suffix
        return tier1_id + NsxPolicyTier1Api.LOCALE_SERVICE_SUFF

    def create_locale_service(self, tier1_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        t1service_def = core_defs.Tier1LocaleServiceDef(
            tier1_id=tier1_id,
            service_id=self._locale_service_id(tier1_id),
            tenant=tenant)
        self._create_or_store(t1service_def)

    def delete_locale_service(self, tier1_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        t1service_def = core_defs.Tier1LocaleServiceDef(
            tier1_id=tier1_id,
            service_id=self._locale_service_id(tier1_id),
            tenant=tenant)
        self._delete_with_retry(t1service_def)

    def get_preferred_edge_paths(self, tier1_id,
                                 tenant=constants.POLICY_INFRA_TENANT):
        services = self.get_locale_tier1_services(tier1_id, tenant=tenant)
        for srv in services:
            if 'preferred_edge_paths' in srv:
                return srv['preferred_edge_paths']

    def set_edge_cluster_path(self, tier1_id, edge_cluster_path,
                              preferred_edge_paths=IGNORE,
                              tenant=constants.POLICY_INFRA_TENANT):
        kwargs = self._get_user_args(
            tier1_id=tier1_id, service_id=self._locale_service_id(tier1_id),
            edge_cluster_path=edge_cluster_path,
            preferred_edge_paths=preferred_edge_paths,
            tenant=tenant
        )
        t1service_def = core_defs.Tier1LocaleServiceDef(**kwargs)
        self._create_or_store(t1service_def)

    def remove_edge_cluster(self, tier1_id,
                            tenant=constants.POLICY_INFRA_TENANT):
        """Reset the path in the locale-service (deleting it is not allowed)"""
        t1service_def = core_defs.Tier1LocaleServiceDef(
            tier1_id=tier1_id,
            service_id=self._locale_service_id(tier1_id),
            edge_cluster_path="",
            tenant=tenant)
        self.policy_api.create_or_update(t1service_def)

    def get_edge_cluster_path(self, tier1_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        t1service_def = core_defs.Tier1LocaleServiceDef(
            tier1_id=tier1_id,
            service_id=self._locale_service_id(tier1_id),
            tenant=tenant)
        try:
            t1service = self.policy_api.get(t1service_def)
            return t1service.get('edge_cluster_path')
        except exceptions.ResourceNotFound:
            return

    def get_edge_cluster_path_by_searching(
            self, tier1_id, tenant=constants.POLICY_INFRA_TENANT):
        """Get the edge_cluster path of a Tier1 router"""
        services = self.get_locale_tier1_services(tier1_id, tenant=tenant)
        for srv in services:
            if 'edge_cluster_path' in srv:
                return srv['edge_cluster_path']

    def get_locale_tier1_services(self, tier1_id,
                                  tenant=constants.POLICY_INFRA_TENANT):
        t1service_def = core_defs.Tier1LocaleServiceDef(
            tier1_id=tier1_id,
            tenant=constants.POLICY_INFRA_TENANT)
        return self.policy_api.list(t1service_def)['results']

    def add_segment_interface(self, tier1_id, interface_id, segment_id,
                              subnets, ipv6_ndra_profile_id=IGNORE,
                              tenant=constants.POLICY_INFRA_TENANT):
        args = {'tier1_id': tier1_id,
                'service_id': self._locale_service_id(tier1_id),
                'interface_id': interface_id,
                'segment_id': segment_id,
                'subnets': subnets,
                'tenant': tenant}

        if ipv6_ndra_profile_id != IGNORE:
            args['ipv6_ndra_profile_id'] = ipv6_ndra_profile_id

        t1interface_def = core_defs.Tier1InterfaceDef(**args)
        self.policy_api.create_or_update(t1interface_def)

    def remove_segment_interface(self, tier1_id, interface_id,
                                 tenant=constants.POLICY_INFRA_TENANT):
        t1interface_def = core_defs.Tier1InterfaceDef(
            tier1_id=tier1_id,
            service_id=self._locale_service_id(tier1_id),
            interface_id=interface_id,
            tenant=tenant)
        self._delete_with_retry(t1interface_def)

    def list_segment_interface(self, tier1_id,
                               tenant=constants.POLICY_INFRA_TENANT,
                               service_id=None):
        t1interface_def = core_defs.Tier1InterfaceDef(
            tier1_id=tier1_id,
            service_id=service_id or self._locale_service_id(tier1_id),
            tenant=tenant)
        return self._list(t1interface_def)

    def get_multicast(self, tier1_id, service_id=None,
                      tenant=constants.POLICY_INFRA_TENANT):
        mcast_def = core_defs.Tier1MulticastDef(
            tier1_id=tier1_id,
            service_id=(service_id or
                        self._locale_service_id(tier1_id)),
            tenant=tenant)
        mcast_data = self.policy_api.get(mcast_def)
        return mcast_data.get('enabled')

    def _set_multicast(self, tier1_id, enabled, service_id, tenant):
        args = {'tier1_id': tier1_id,
                'service_id': (service_id or
                               self._locale_service_id(tier1_id)),
                'enabled': enabled,
                'tenant': tenant}
        mcast_def = core_defs.Tier1MulticastDef(**args)
        self._create_or_store(mcast_def)

    def enable_multicast(self, tier1_id, service_id=None,
                         tenant=constants.POLICY_INFRA_TENANT):
        self._set_multicast(tier1_id, True, service_id, tenant)

    def disable_multicast(self, tier1_id, service_id=None,
                          tenant=constants.POLICY_INFRA_TENANT):
        self._set_multicast(tier1_id, False, service_id, tenant)

    def get_realized_state(self, tier1_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        return self._get_realized_state(tier1_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, tier1_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        if self.nsx_api:
            # Use MP search api to find the LR ID as it is faster
            return self._get_realized_id_using_search(
                self.get_path(tier1_id, tenant=tenant),
                self.nsx_api.logical_router.resource_type,
                resource_def=tier1_def, entity_type=entity_type)
        return self._get_realized_id(tier1_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, tier1_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        return self._get_realization_info(tier1_def, silent=silent,
                                          entity_type=entity_type)

    def get_realized_router_port(self, tier1_id, silent=False,
                                 tenant=constants.POLICY_INFRA_TENANT):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        ports = self._get_realization_info(
            tier1_def, entity_type='RealizedLogicalRouterPort',
            all_result=True, silent=silent)
        return ports

    def wait_until_realized(self, tier1_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        return self._wait_until_realized(tier1_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)

    @check_allowed_passthrough
    def update_transport_zone(self, tier1_id, transport_zone_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        """Use the pass-through api to update the TZ zone on the NSX router"""
        realization_info = self.wait_until_realized(
            tier1_id, entity_type='RealizedLogicalRouter', tenant=tenant)

        nsx_router_uuid = self.get_realized_id(
            tier1_id, tenant=tenant, realization_info=realization_info)
        self.nsx_api.logical_router.update(
            nsx_router_uuid,
            transport_zone_id=transport_zone_id)

    @check_allowed_passthrough
    def _get_realized_downlink_port(
        self, tier1_id, segment_id,
        tenant=constants.POLICY_INFRA_TENANT,
        sleep=None, max_attempts=None):
        """Return the realized ID of a tier1 downlink port of a segment

        If not found, wait until it has been realized
        """
        if sleep is None:
            sleep = self.nsxlib_config.realization_wait_sec
        if max_attempts is None:
            max_attempts = self.nsxlib_config.realization_max_attempts

        tier1_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        path = tier1_def.get_resource_full_path()

        test_num = 0
        while test_num < max_attempts:
            # get all the realized resources of the tier1
            entities = self.policy_api.get_realized_entities(path)
            for e in entities:
                # Look for router ports
                if (e['entity_type'] == 'RealizedLogicalRouterPort' and
                    e['state'] == constants.STATE_REALIZED):
                    # Get the NSX port to check if its the downlink port
                    port = self.nsx_api.logical_router_port.get(
                        e['realization_specific_identifier'])
                    # compare the segment ID to the port display name as this
                    # is the way policy sets it
                    port_type = port.get('resource_type')
                    if (port_type == nsx_constants.LROUTERPORT_DOWNLINK and
                        segment_id in port.get('display_name', '')):
                        return port['id']
            eventlet.sleep(sleep)
            test_num += 1

        raise exceptions.DetailedRealizationTimeoutError(
            resource_type='Tier1',
            resource_id=tier1_id,
            realized_type="downlink port",
            related_type="segment",
            related_id=segment_id,
            attempts=max_attempts,
            sleep=sleep)

    @check_allowed_passthrough
    def set_dhcp_relay(self, tier1_id, segment_id, relay_service_uuid,
                       tenant=constants.POLICY_INFRA_TENANT):
        """Set relay service on the nsx logical router port

        Using passthrough api, as the policy api does not support this yet
        """
        downlink_port_id = self._get_realized_downlink_port(
            tier1_id, segment_id, tenant=tenant)
        self.nsx_api.logical_router_port.update(
            downlink_port_id, relay_service_uuid=relay_service_uuid)

    def set_standby_relocation(self, tier1_id,
                               enable_standby_relocation=True,
                               tenant=constants.POLICY_INFRA_TENANT):
        """Set the flag for standby relocation on the Tier1 router

        """
        return self.update(tier1_id,
                           enable_standby_relocation=enable_standby_relocation,
                           tenant=tenant)


class NsxPolicyTier0Api(NsxPolicyResourceBase):
    """NSX Tier0 API """
    @property
    def entry_def(self):
        return core_defs.Tier0Def

    def create_or_overwrite(self, name, tier0_id=None,
                            description=IGNORE,
                            ha_mode=constants.ACTIVE_ACTIVE,
                            failover_mode=constants.NON_PREEMPTIVE,
                            dhcp_config=IGNORE,
                            force_whitelisting=IGNORE,
                            default_rule_logging=IGNORE,
                            transit_subnets=IGNORE,
                            disable_firewall=IGNORE,
                            ipv6_ndra_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        tier0_id = self._init_obj_uuid(tier0_id)
        tier0_def = self._init_def(tier0_id=tier0_id,
                                   name=name,
                                   description=description,
                                   ha_mode=ha_mode,
                                   failover_mode=failover_mode,
                                   dhcp_config=dhcp_config,
                                   force_whitelisting=force_whitelisting,
                                   default_rule_logging=default_rule_logging,
                                   transit_subnets=transit_subnets,
                                   disable_firewall=disable_firewall,
                                   ipv6_ndra_profile_id=ipv6_ndra_profile_id,
                                   tags=tags,
                                   tenant=tenant)
        self.policy_api.create_or_update(tier0_def)
        return tier0_id

    def delete(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        self._delete_with_retry(tier0_def)

    def get(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self.policy_api.get(tier0_def, silent=silent)

    def get_path(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return tier0_def.get_resource_full_path()

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        tier0_def = self.entry_def(tenant=tenant)
        return self._list(tier0_def)

    def update(self, tier0_id, name=IGNORE, description=IGNORE,
               failover_mode=IGNORE,
               dhcp_config=IGNORE,
               force_whitelisting=IGNORE,
               default_rule_logging=IGNORE,
               transit_subnets=IGNORE,
               disable_firewall=IGNORE,
               ipv6_ndra_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        self._update(tier0_id=tier0_id,
                     name=name,
                     description=description,
                     failover_mode=failover_mode,
                     dhcp_config=dhcp_config,
                     force_whitelisting=force_whitelisting,
                     default_rule_logging=default_rule_logging,
                     transit_subnets=transit_subnets,
                     disable_firewall=disable_firewall,
                     ipv6_ndra_profile_id=ipv6_ndra_profile_id,
                     tags=tags,
                     tenant=tenant)

    def get_locale_services(self, tier0_id,
                            tenant=constants.POLICY_INFRA_TENANT):
        t0service_def = core_defs.Tier0LocaleServiceDef(
            tier0_id=tier0_id,
            tenant=constants.POLICY_INFRA_TENANT)
        return self.policy_api.list(t0service_def)['results']

    def get_edge_cluster_path(self, tier0_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        """Get the edge_cluster path of a Tier0 router"""
        services = self.get_locale_services(tier0_id, tenant=tenant)
        for srv in services:
            if 'edge_cluster_path' in srv:
                return srv['edge_cluster_path']

    @check_allowed_passthrough
    def get_overlay_transport_zone(
        self, tier0_id,
        tenant=constants.POLICY_INFRA_TENANT):
        """Use the pass-through api to get the TZ zone of the NSX tier0"""
        realization_info = self.wait_until_realized(
            tier0_id, entity_type='RealizedLogicalRouter', tenant=tenant)
        nsx_router_uuid = self.get_realized_id(
            tier0_id, tenant=tenant,
            realization_info=realization_info)
        return self.nsx_api.router.get_tier0_router_overlay_tz(
            nsx_router_uuid)

    def get_realized_state(self, tier0_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self._get_realized_state(tier0_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, tier0_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self._get_realized_id(tier0_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, tier0_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self._get_realization_info(tier0_def, entity_type=entity_type,
                                          silent=silent)

    def wait_until_realized(self, tier0_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        tier0_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self._wait_until_realized(tier0_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)

    @check_allowed_passthrough
    def get_transport_zones(self, tier0_id,
                            tenant=constants.POLICY_INFRA_TENANT):
        """Return a list of the transport zones IDs connected to the tier0

        Currently this is supported only with the passthrough api
        """
        realization_info = self.wait_until_realized(
            tier0_id, entity_type='RealizedLogicalRouter', tenant=tenant)
        nsx_router_uuid = self.get_realized_id(
            tier0_id, tenant=tenant,
            realization_info=realization_info)
        return self.nsx_api.router.get_tier0_router_tz(
            nsx_router_uuid)

    def _get_uplink_subnets(self, tier0_id,
                            tenant=constants.POLICY_INFRA_TENANT):
        subnets = []
        services = self.get_locale_services(tier0_id, tenant=tenant)
        for srv in services:
            # get the interfaces of this service
            t0interface_def = core_defs.Tier0InterfaceDef(
                tier0_id=tier0_id,
                service_id=srv['id'],
                tenant=constants.POLICY_INFRA_TENANT)
            interfaces = self.policy_api.list(
                t0interface_def).get('results', [])
            for interface in interfaces:
                if interface.get('type') == 'EXTERNAL':
                    subnets.extend(interface.get('subnets', []))
        return subnets

    def get_uplink_ips(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        """Return a link of all uplink ips of this tier0 router"""
        subnets = self._get_uplink_subnets(tier0_id, tenant=tenant)
        uplink_ips = []
        for subnet in subnets:
            uplink_ips.extend(subnet.get('ip_addresses', []))
        return uplink_ips

    def get_uplink_cidrs(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        """Return a link of all uplink cidrs of this tier0 router"""
        subnets = self._get_uplink_subnets(tier0_id, tenant=tenant)
        cidrs = []
        for subnet in subnets:
            for ip_address in subnet.get('ip_addresses'):
                cidrs.append('%s/%s' % (ip_address,
                                        subnet.get('prefix_len')))
        return cidrs

    def get_bgp_config(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        services = self.get_locale_services(tier0_id, tenant=tenant)
        for srv in services:
            bgpconfig_def = core_defs.BgpRoutingConfigDef(
                tier0_id=tier0_id,
                service_id=srv['id'],
                tenant=constants.POLICY_INFRA_TENANT)
            try:
                return self.policy_api.get(bgpconfig_def)
            except exceptions.ResourceNotFound:
                continue

    def build_route_redistribution_rule(self, name=None, types=None,
                                        route_map_path=None):
        return core_defs.Tier0RouteRedistributionRule(
            name, types, route_map_path)

    def build_route_redistribution_config(self, enabled=None, rules=None):
        return core_defs.Tier0RouteRedistributionConfig(enabled, rules)

    def get_route_redistribution_config(self, tier0_id,
                                        tenant=constants.POLICY_INFRA_TENANT):
        services = self.get_locale_services(tier0_id, tenant=tenant)
        for srv in services:
            if srv.get('route_redistribution_config'):
                return srv['route_redistribution_config']

    def update_route_redistribution_config(
        self, tier0_id, redistribution_config, service_id=None,
        tenant=constants.POLICY_INFRA_TENANT):
        if not service_id:
            # Update on the first locale service
            services = self.get_locale_services(tier0_id, tenant=tenant)
            if len(services) > 0:
                service_id = services[0]['id']
        if not service_id:
            err_msg = (_("Cannot update route redistribution config without "
                         "locale service on Tier0 router"))
            raise exceptions.ManagerError(details=err_msg)

        service_def = core_defs.Tier0LocaleServiceDef(
            nsx_version=self.version,
            tier0_id=tier0_id,
            service_id=service_id,
            route_redistribution_config=redistribution_config,
            tenant=tenant)
        self.policy_api.create_or_update(service_def)


class NsxPolicyTier0BgpApi(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.BgpRoutingConfigDef

    def delete(self, tier0_id, service_id,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = _("This action is currently not supported")
        raise exceptions.ManagerError(details=err_msg)

    def create_or_overwrite(self, tier0_id, service_id,
                            name=IGNORE,
                            description=IGNORE,
                            ecmp=IGNORE,
                            enabled=IGNORE,
                            graceful_restart_config=IGNORE,
                            inter_sr_ibgp=IGNORE,
                            local_as_num=IGNORE,
                            multipath_relax=IGNORE,
                            route_aggregations=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        bgp_config_def = self._init_def(
            name=name,
            description=description,
            tier0_id=tier0_id,
            service_id=service_id,
            ecmp=ecmp,
            enabled=enabled,
            graceful_restart_config=graceful_restart_config,
            inter_sr_ibgp=inter_sr_ibgp,
            local_as_num=local_as_num,
            multipath_relax=multipath_relax,
            route_aggregations=route_aggregations,
            tags=tags,
            tenant=tenant)
        self._create_or_store(bgp_config_def)

    def get(self, tier0_id, service_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        bgp_config_def = self.entry_def(
            tier0_id=tier0_id, service_id=service_id, tenant=tenant)
        return self.policy_api.get(bgp_config_def, silent=silent)

    def list(self, tier0_id, service_id,
             tenant=constants.POLICY_INFRA_TENANT):
        err_msg = _("This action is currently not supported")
        raise exceptions.ManagerError(details=err_msg)

    def update(self, tier0_id, service_id,
               name=IGNORE,
               description=IGNORE,
               ecmp=IGNORE,
               enabled=IGNORE,
               graceful_restart_config=IGNORE,
               inter_sr_ibgp=IGNORE,
               local_as_num=IGNORE,
               multipath_relax=IGNORE,
               route_aggregations=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT,
               put=False,
               revision=None):
        return self._update(name=name,
                            description=description,
                            tier0_id=tier0_id,
                            service_id=service_id,
                            ecmp=ecmp,
                            enabled=enabled,
                            graceful_restart_config=graceful_restart_config,
                            inter_sr_ibgp=inter_sr_ibgp,
                            local_as_num=local_as_num,
                            multipath_relax=multipath_relax,
                            route_aggregations=route_aggregations,
                            tags=tags,
                            tenant=tenant,
                            put=put,
                            revision=revision)


class NsxPolicyTier0NatRuleApi(NsxPolicyResourceBase):
    DEFAULT_NAT_ID = 'USER'

    @property
    def entry_def(self):
        return core_defs.Tier0NatRule

    def create_or_overwrite(self, name, tier0_id,
                            nat_id=DEFAULT_NAT_ID,
                            nat_rule_id=None,
                            description=IGNORE,
                            source_network=IGNORE,
                            destination_network=IGNORE,
                            translated_network=IGNORE,
                            firewall_match=constants.NAT_FIREWALL_MATCH_BYPASS,
                            action=IGNORE,
                            sequence_number=IGNORE,
                            logging=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT,
                            enabled=IGNORE):

        nat_rule_id = self._init_obj_uuid(nat_rule_id)
        nat_rule_def = self._init_def(tier0_id=tier0_id,
                                      nat_id=nat_id,
                                      nat_rule_id=nat_rule_id,
                                      name=name,
                                      description=description,
                                      source_network=source_network,
                                      destination_network=destination_network,
                                      translated_network=translated_network,
                                      firewall_match=firewall_match,
                                      action=action,
                                      sequence_number=sequence_number,
                                      logging=logging,
                                      tags=tags,
                                      tenant=tenant,
                                      enabled=enabled)
        self._create_or_store(nat_rule_def)
        return nat_rule_id

    def delete(self, tier0_id, nat_rule_id, nat_id=DEFAULT_NAT_ID,
               tenant=constants.POLICY_INFRA_TENANT):
        nat_rule_def = self.entry_def(tier0_id=tier0_id, nat_id=nat_id,
                                      nat_rule_id=nat_rule_id, tenant=tenant)
        self._delete_with_retry(nat_rule_def)

    def get(self, tier0_id, nat_rule_id, nat_id=DEFAULT_NAT_ID,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        nat_rule_def = self.entry_def(tier0_id=tier0_id, nat_id=nat_id,
                                      nat_rule_id=nat_rule_id, tenant=tenant)
        return self.policy_api.get(nat_rule_def, silent=silent)

    def list(self, tier0_id, nat_id=DEFAULT_NAT_ID,
             tenant=constants.POLICY_INFRA_TENANT):
        nat_rule_def = self.entry_def(tier0_id=tier0_id, nat_id=nat_id,
                                      tenant=tenant)
        return self._list(nat_rule_def)

    def update(self, tier0_id, nat_rule_id,
               nat_id=DEFAULT_NAT_ID,
               name=IGNORE,
               description=IGNORE,
               source_network=IGNORE,
               destination_network=IGNORE,
               translated_network=IGNORE,
               firewall_match=IGNORE,
               action=IGNORE,
               sequence_number=IGNORE,
               logging=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT,
               enabled=IGNORE):
        self._update(tier0_id=tier0_id,
                     nat_id=nat_id,
                     nat_rule_id=nat_rule_id,
                     name=name,
                     description=description,
                     source_network=source_network,
                     destination_network=destination_network,
                     translated_network=translated_network,
                     firewall_match=firewall_match,
                     action=action,
                     sequence_number=sequence_number,
                     logging=logging,
                     tags=tags,
                     tenant=tenant,
                     enabled=enabled)


class NsxPolicyTier1NatRuleApi(NsxPolicyResourceBase):
    DEFAULT_NAT_ID = 'USER'

    @property
    def entry_def(self):
        return core_defs.Tier1NatRule

    def create_or_overwrite(self, name, tier1_id,
                            nat_id=DEFAULT_NAT_ID,
                            nat_rule_id=None,
                            description=IGNORE,
                            source_network=IGNORE,
                            destination_network=IGNORE,
                            translated_network=IGNORE,
                            firewall_match=constants.NAT_FIREWALL_MATCH_BYPASS,
                            action=IGNORE,
                            sequence_number=IGNORE,
                            logging=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT,
                            enabled=IGNORE):

        nat_rule_id = self._init_obj_uuid(nat_rule_id)
        nat_rule_def = self._init_def(tier1_id=tier1_id,
                                      nat_id=nat_id,
                                      nat_rule_id=nat_rule_id,
                                      name=name,
                                      description=description,
                                      source_network=source_network,
                                      destination_network=destination_network,
                                      translated_network=translated_network,
                                      firewall_match=firewall_match,
                                      action=action,
                                      sequence_number=sequence_number,
                                      logging=logging,
                                      tags=tags,
                                      tenant=tenant,
                                      enabled=enabled)
        self._create_or_store(nat_rule_def)
        return nat_rule_id

    def delete(self, tier1_id, nat_rule_id, nat_id=DEFAULT_NAT_ID,
               tenant=constants.POLICY_INFRA_TENANT):
        nat_rule_def = self.entry_def(tier1_id=tier1_id, nat_id=nat_id,
                                      nat_rule_id=nat_rule_id, tenant=tenant)
        self._delete_or_store(nat_rule_def)

    def get(self, tier1_id, nat_rule_id, nat_id=DEFAULT_NAT_ID,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        nat_rule_def = self.entry_def(tier1_id=tier1_id, nat_id=nat_id,
                                      nat_rule_id=nat_rule_id, tenant=tenant)
        return self.policy_api.get(nat_rule_def, silent=silent)

    def list(self, tier1_id, nat_id=DEFAULT_NAT_ID,
             tenant=constants.POLICY_INFRA_TENANT):
        nat_rule_def = self.entry_def(tier1_id=tier1_id, nat_id=nat_id,
                                      tenant=tenant)
        return self._list(nat_rule_def)

    def update(self, tier1_id, nat_rule_id,
               nat_id=DEFAULT_NAT_ID,
               name=IGNORE,
               description=IGNORE,
               source_network=IGNORE,
               destination_network=IGNORE,
               translated_network=IGNORE,
               firewall_match=IGNORE,
               action=IGNORE,
               sequence_number=IGNORE,
               logging=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT,
               enabled=IGNORE):
        self._update(tier1_id=tier1_id,
                     nat_id=nat_id,
                     nat_rule_id=nat_rule_id,
                     name=name,
                     description=description,
                     source_network=source_network,
                     destination_network=destination_network,
                     translated_network=translated_network,
                     firewall_match=firewall_match,
                     action=action,
                     sequence_number=sequence_number,
                     logging=logging,
                     tags=tags,
                     tenant=tenant,
                     enabled=enabled)


class NSXPolicyTier0StaticRouteApi(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.Tier0StaticRoute

    def create_or_overwrite(self, name, tier0_id,
                            static_route_id=None,
                            description=IGNORE,
                            network=IGNORE,
                            next_hop=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT,
                            scope=IGNORE):
        static_route_id = self._init_obj_uuid(static_route_id)
        static_route_def = self._init_def(tier0_id=tier0_id,
                                          static_route_id=static_route_id,
                                          name=name,
                                          description=description,
                                          network=network,
                                          next_hop=next_hop,
                                          tags=tags,
                                          tenant=tenant,
                                          scope=scope)
        self._create_or_store(static_route_def)
        return static_route_id

    def delete(self, tier0_id, static_route_id,
               tenant=constants.POLICY_INFRA_TENANT):
        static_route_def = self.entry_def(tier0_id=tier0_id,
                                          static_route_id=static_route_id,
                                          tenant=tenant)
        self._delete_with_retry(static_route_def)

    def get(self, tier0_id, static_route_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        static_route_def = self.entry_def(tier0_id=tier0_id,
                                          static_route_id=static_route_id,
                                          tenant=tenant)
        return self.policy_api.get(static_route_def, silent=silent)

    def list(self, tier0_id,
             tenant=constants.POLICY_INFRA_TENANT):
        static_route_def = self.entry_def(tier0_id=tier0_id,
                                          tenant=tenant)
        return self._list(static_route_def)

    def update(self, tier0_id, static_route_id,
               name=IGNORE,
               description=IGNORE,
               network=IGNORE,
               next_hop=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(tier0_id=tier0_id,
                     static_route_id=static_route_id,
                     name=name,
                     description=description,
                     network=network,
                     next_hop=next_hop,
                     tags=tags,
                     tenant=tenant)


class NsxPolicyTier1StaticRouteApi(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.Tier1StaticRoute

    def create_or_overwrite(self, name, tier1_id,
                            static_route_id=None,
                            description=IGNORE,
                            network=IGNORE,
                            next_hop=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        static_route_id = self._init_obj_uuid(static_route_id)
        static_route_def = self._init_def(tier1_id=tier1_id,
                                          static_route_id=static_route_id,
                                          name=name,
                                          description=description,
                                          network=network,
                                          next_hop=next_hop,
                                          tags=tags,
                                          tenant=tenant)
        self._create_or_store(static_route_def)
        return static_route_id

    def delete(self, tier1_id, static_route_id,
               tenant=constants.POLICY_INFRA_TENANT):
        static_route_def = self.entry_def(tier1_id=tier1_id,
                                          static_route_id=static_route_id,
                                          tenant=tenant)
        self._delete_with_retry(static_route_def)

    def get(self, tier1_id, static_route_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        static_route_def = self.entry_def(tier1_id=tier1_id,
                                          static_route_id=static_route_id,
                                          tenant=tenant)
        return self.policy_api.get(static_route_def, silent=silent)

    def list(self, tier1_id,
             tenant=constants.POLICY_INFRA_TENANT):
        static_route_def = self.entry_def(tier1_id=tier1_id,
                                          tenant=tenant)
        return self._list(static_route_def)

    def update(self, tier1_id, static_route_id,
               name=IGNORE,
               description=IGNORE,
               network=IGNORE,
               next_hop=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(tier1_id=tier1_id,
                     static_route_id=static_route_id,
                     name=name,
                     description=description,
                     network=network,
                     next_hop=next_hop,
                     tags=tags,
                     tenant=tenant)

    def wait_until_realized(self, tier1_id, static_route_id,
                            entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        static_route_def = self.entry_def(tier1_id=tier1_id,
                                          static_route_id=static_route_id,
                                          tenant=tenant)
        return self._wait_until_realized(static_route_def,
                                         entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)


class NsxPolicyTier1SegmentApi(NsxPolicyResourceBase):
    """NSX Tier1 Segment API """
    @property
    def entry_def(self):
        return core_defs.Tier1SegmentDef

    def build_subnet(self, gateway_address, dhcp_ranges=None,
                     dhcp_config=None):
        return core_defs.Subnet(gateway_address, dhcp_ranges, dhcp_config)

    def build_dhcp_config_v4(self, server_address, dns_servers=None,
                             lease_time=None, options=None):
        return core_defs.SegmentDhcpConfigV4(server_address, dns_servers,
                                             lease_time, options)

    def build_dhcp_config_v6(self, server_address, dns_servers=None,
                             lease_time=None, domain_names=None):
        return core_defs.SegmentDhcpConfigV6(server_address, dns_servers,
                                             lease_time, domain_names)

    def create_or_overwrite(self, name, tier1_id,
                            segment_id=None,
                            description=IGNORE,
                            subnets=IGNORE,
                            dhcp_config=IGNORE,
                            dns_domain_name=IGNORE,
                            vlan_ids=IGNORE,
                            default_rule_logging=IGNORE,
                            ip_pool_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        segment_id = self._init_obj_uuid(segment_id)
        segment_def = self._init_def(tier1_id=tier1_id,
                                     segment_id=segment_id,
                                     name=name,
                                     description=description,
                                     subnets=subnets,
                                     dhcp_config=dhcp_config,
                                     dns_domain_name=dns_domain_name,
                                     vlan_ids=vlan_ids,
                                     default_rule_logging=default_rule_logging,
                                     ip_pool_id=ip_pool_id,
                                     tags=tags,
                                     tenant=tenant)
        self._create_or_store(segment_def)
        return segment_id

    def delete(self, tier1_id, segment_id,
               tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(tier1_id=tier1_id,
                                     segment_id=segment_id,
                                     tenant=tenant)
        self._delete_with_retry(segment_def)

    def get(self, tier1_id, segment_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        segment_def = self.entry_def(tier1_id=tier1_id,
                                     segment_id=segment_id,
                                     tenant=tenant)
        return self.policy_api.get(segment_def, silent=silent)

    def list(self, tier1_id, tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(tier1_id=tier1_id, tenant=tenant)
        return self._list(segment_def)

    def update(self, tier1_id, segment_id,
               name=IGNORE,
               description=IGNORE,
               subnets=IGNORE,
               dhcp_config=IGNORE,
               dns_domain_name=IGNORE,
               vlan_ids=IGNORE,
               default_rule_logging=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        self._update(tier1_id=tier1_id,
                     segment_id=segment_id,
                     name=name,
                     description=description,
                     subnets=subnets,
                     dhcp_config=dhcp_config,
                     dns_domain_name=dns_domain_name,
                     vlan_ids=vlan_ids,
                     default_rule_logging=default_rule_logging,
                     tags=tags,
                     tenant=tenant)


class NsxPolicySegmentApi(NsxPolicyResourceBase):
    """NSX Infra Segment API """
    @property
    def entry_def(self):
        return core_defs.SegmentDef

    def build_subnet(self, gateway_address, dhcp_ranges=None,
                     dhcp_config=None):
        return core_defs.Subnet(gateway_address, dhcp_ranges, dhcp_config)

    def build_dhcp_config_v4(self, server_address, dns_servers=None,
                             lease_time=None, options=None):
        return core_defs.SegmentDhcpConfigV4(server_address, dns_servers,
                                             lease_time, options)

    def build_dhcp_config_v6(self, server_address, dns_servers=None,
                             lease_time=None, domain_names=None):
        return core_defs.SegmentDhcpConfigV6(server_address, dns_servers,
                                             lease_time, domain_names)

    def create_or_overwrite(self, name,
                            segment_id=None,
                            tier1_id=IGNORE,
                            tier0_id=IGNORE,
                            description=IGNORE,
                            subnets=IGNORE,
                            dns_domain_name=IGNORE,
                            vlan_ids=IGNORE,
                            transport_zone_id=IGNORE,
                            ip_pool_id=IGNORE,
                            metadata_proxy_id=IGNORE,
                            dhcp_server_config_id=IGNORE,
                            admin_state=IGNORE,
                            ls_id=IGNORE,
                            unique_id=IGNORE,
                            ep_id=IGNORE,
                            overlay_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        if tier0_id != IGNORE and tier1_id != IGNORE:
            err_msg = (_("Cannot connect Segment to a Tier-0 and Tier-1 "
                         "Gateway simultaneously"))
            raise exceptions.InvalidInput(details=err_msg)

        segment_id = self._init_obj_uuid(segment_id)
        segment_def = self._init_def(
            segment_id=segment_id,
            name=name,
            description=description,
            tier1_id=tier1_id,
            tier0_id=tier0_id,
            subnets=subnets,
            dns_domain_name=dns_domain_name,
            vlan_ids=vlan_ids,
            transport_zone_id=transport_zone_id,
            ip_pool_id=ip_pool_id,
            metadata_proxy_id=metadata_proxy_id,
            dhcp_server_config_id=dhcp_server_config_id,
            admin_state=admin_state,
            ls_id=ls_id,
            unique_id=unique_id,
            ep_id=ep_id,
            overlay_id=overlay_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(segment_def)
        return segment_id

    def delete(self, segment_id,
               tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)

        @utils.retry_upon_exception(
            exceptions.NsxSegemntWithVM,
            delay=self.nsxlib_config.realization_wait_sec,
            max_attempts=self.nsxlib_config.realization_max_attempts)
        def do_delete():
            self._delete_with_retry(segment_def)

        do_delete()

    def get(self, segment_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self.policy_api.get(segment_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(tenant=tenant)
        return self._list(segment_def)

    def update(self, segment_id, name=IGNORE, description=IGNORE,
               tier1_id=IGNORE, tier0_id=IGNORE, subnets=IGNORE,
               dns_domain_name=IGNORE,
               vlan_ids=IGNORE, metadata_proxy_id=IGNORE,
               dhcp_server_config_id=IGNORE, admin_state=IGNORE,
               tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT):

        self._update(segment_id=segment_id,
                     name=name,
                     description=description,
                     tier1_id=tier1_id,
                     tier0_id=tier0_id,
                     subnets=subnets,
                     dns_domain_name=dns_domain_name,
                     vlan_ids=vlan_ids,
                     metadata_proxy_id=metadata_proxy_id,
                     dhcp_server_config_id=dhcp_server_config_id,
                     admin_state=admin_state,
                     tags=tags,
                     tenant=tenant)

    def remove_connectivity_and_subnets(
        self, segment_id,
        tenant=constants.POLICY_INFRA_TENANT):
        """Disconnect a segment from a router and remove its subnets.

        PATCH does not support this action so PUT is used for this
        """
        # Get the current segment and update it
        segment = self.get(segment_id)
        segment['subnets'] = None
        segment['connectivity_path'] = None

        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        path = segment_def.get_resource_path()

        self.policy_api.client.update(path, segment)

    def remove_connectivity_path(self, segment_id,
                                 tenant=constants.POLICY_INFRA_TENANT):
        """Disconnect a segment from a router.

        PATCH does not support this action so PUT is used for this
        """
        # Get the current segment and update it
        segment = self.get(segment_id)
        segment['connectivity_path'] = None

        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        path = segment_def.get_resource_path()

        self.policy_api.client.update(path, segment)

    def get_realized_state(self, segment_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self._get_realized_state(segment_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, segment_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self._get_realized_id(segment_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_path(self, segment_id, tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return segment_def.get_resource_full_path()

    def get_realized_logical_switch_id(self, segment_id,
                                       tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        entity_type = 'RealizedLogicalSwitch'
        if self.nsx_api:
            # Use MP search api to find the LS ID as it is faster
            return self._get_realized_id_using_search(
                self.get_path(segment_id, tenant=tenant),
                self.nsx_api.logical_switch.resource_type,
                resource_def=segment_def, entity_type=entity_type)

        realization_info = self._wait_until_realized(
            segment_def, entity_type=entity_type)
        return self._get_realized_id(segment_def,
                                     realization_info=realization_info)

    def get_realization_info(self, segment_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self._get_realization_info(segment_def,
                                          entity_type=entity_type,
                                          silent=silent)

    def wait_until_realized(self, segment_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self._wait_until_realized(segment_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)

    def wait_until_state_successful(self, segment_id,
                                    tenant=constants.POLICY_INFRA_TENANT,
                                    sleep=None, max_attempts=None,
                                    with_refresh=False):
        segment_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        self._wait_until_state_successful(segment_def, sleep=sleep,
                                          max_attempts=max_attempts,
                                          with_refresh=with_refresh)

    @check_allowed_passthrough
    def set_admin_state(self, segment_id, admin_state,
                        tenant=constants.POLICY_INFRA_TENANT):
        """Set the segment admin state using the passthrough/policy api"""
        if (version.LooseVersion(self.version) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_3_0_0)):
            return self.update(segment_id, admin_state=admin_state,
                               tenant=tenant)

        realization_info = self.wait_until_realized(
            segment_id, entity_type='RealizedLogicalSwitch', tenant=tenant)

        nsx_ls_uuid = self.get_realized_id(
            segment_id, tenant=tenant, realization_info=realization_info)
        self.nsx_api.logical_switch.update(
            nsx_ls_uuid,
            admin_state=admin_state)

    def get_transport_zone_id(self, segment_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        segment = self.get(segment_id, tenant=tenant)
        tz_path = segment.get('transport_zone_path')
        if tz_path:
            return p_utils.path_to_id(tz_path)


class NsxPolicySegmentPortApi(NsxPolicyResourceBase):
    """NSX Segment Port API """
    @property
    def entry_def(self):
        return core_defs.SegmentPortDef

    def build_address_binding(self, ip_address, mac_address,
                              vlan_id=None):
        return core_defs.PortAddressBinding(ip_address,
                                            mac_address,
                                            vlan_id)

    def create_or_overwrite(self, name,
                            segment_id,
                            port_id=None,
                            description=IGNORE,
                            address_bindings=IGNORE,
                            attachment_type=IGNORE,
                            vif_id=IGNORE,
                            app_id=IGNORE,
                            context_id=IGNORE,
                            traffic_tag=IGNORE,
                            allocate_addresses=IGNORE,
                            hyperbus_mode=IGNORE,
                            admin_state=IGNORE,
                            init_state=IGNORE,
                            extra_configs=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        port_id = self._init_obj_uuid(port_id)
        port_def = self._init_def(segment_id=segment_id,
                                  port_id=port_id,
                                  name=name,
                                  description=description,
                                  address_bindings=address_bindings,
                                  attachment_type=attachment_type,
                                  vif_id=vif_id,
                                  app_id=app_id,
                                  context_id=context_id,
                                  traffic_tag=traffic_tag,
                                  allocate_addresses=allocate_addresses,
                                  hyperbus_mode=hyperbus_mode,
                                  admin_state=admin_state,
                                  init_state=init_state,
                                  extra_configs=extra_configs,
                                  tags=tags,
                                  tenant=tenant)
        self._create_or_store(port_def)
        return port_id

    def delete(self, segment_id, port_id,
               tenant=constants.POLICY_INFRA_TENANT):
        port_def = self.entry_def(segment_id=segment_id,
                                  port_id=port_id,
                                  tenant=tenant)
        self._delete_with_retry(port_def)

    def get(self, segment_id, port_id,
            tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        port_def = self.entry_def(segment_id=segment_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self.policy_api.get(port_def, silent=silent)

    def list(self, segment_id, tenant=constants.POLICY_INFRA_TENANT):
        port_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self._list(port_def)

    def update(self, segment_id, port_id,
               name=IGNORE,
               description=IGNORE,
               address_bindings=IGNORE,
               hyperbus_mode=IGNORE,
               admin_state=IGNORE,
               extra_configs=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        self._update(segment_id=segment_id,
                     port_id=port_id,
                     name=name,
                     description=description,
                     address_bindings=address_bindings,
                     hyperbus_mode=hyperbus_mode,
                     admin_state=admin_state,
                     extra_configs=extra_configs,
                     tags=tags,
                     tenant=tenant)

    def detach(self, segment_id, port_id, vif_id=None, tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        """Reset the attachment with or without a vif_id"""
        # Due to platform limitation, PUT should be used here and not PATCH
        port_def = self.entry_def(
            segment_id=segment_id,
            port_id=port_id,
            tenant=tenant)
        path = port_def.get_resource_path()

        @utils.retry_upon_exception(
            exceptions.StaleRevision,
            max_attempts=self.policy_api.client.max_attempts)
        def _detach():
            port = self.policy_api.get(port_def)
            if vif_id:
                port['attachment'] = {'id': vif_id}
            else:
                port['attachment'] = None
            if tags != IGNORE:
                port['tags'] = tags
            self.policy_api.client.update(path, port)

        _detach()

    def attach(self, segment_id, port_id,
               attachment_type,
               vif_id,
               allocate_addresses=None,
               app_id=None,
               context_id=None,
               traffic_tag=None,
               hyperbus_mode=IGNORE,
               extra_configs=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        self._update(segment_id=segment_id,
                     port_id=port_id,
                     attachment_type=attachment_type,
                     allocate_addresses=allocate_addresses,
                     vif_id=vif_id,
                     app_id=app_id,
                     context_id=context_id,
                     traffic_tag=traffic_tag,
                     hyperbus_mode=hyperbus_mode,
                     extra_configs=extra_configs,
                     tags=tags,
                     tenant=tenant)

    def get_realized_state(self, segment_id, port_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        port_def = self.entry_def(segment_id=segment_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self._get_realized_state(port_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, segment_id, port_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        port_def = self.entry_def(segment_id=segment_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self._get_realized_id(port_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, segment_id, port_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        port_def = self.entry_def(segment_id=segment_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self._get_realization_info(port_def, entity_type=entity_type,
                                          silent=silent)

    def wait_until_realized(self, segment_id, port_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        port_def = self.entry_def(segment_id=segment_id, port_id=port_id,
                                  tenant=tenant)
        return self._wait_until_realized(port_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)

    @check_allowed_passthrough
    def set_admin_state(self, segment_id, port_id, admin_state,
                        tenant=constants.POLICY_INFRA_TENANT):
        """Set the segment port admin state using the passthrough/policy api"""
        if (version.LooseVersion(self.version) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_3_0_0)):
            return self.update(segment_id, port_id, admin_state=admin_state,
                               tenant=tenant)

        realization_info = self.wait_until_realized(
            segment_id, port_id, entity_type='RealizedLogicalPort',
            tenant=tenant)

        nsx_lp_uuid = self.get_realized_id(
            segment_id, port_id, tenant=tenant,
            realization_info=realization_info)
        self.nsx_api.logical_port.update(
            nsx_lp_uuid, False,
            admin_state=admin_state)


class SegmentProfilesBindingMapBaseApi(NsxPolicyResourceBase):

    def delete(self, segment_id, map_id=DEFAULT_MAP_ID,
               tenant=constants.POLICY_INFRA_TENANT):
        map_def = self.entry_def(segment_id=segment_id,
                                 map_id=map_id,
                                 tenant=tenant)
        self._delete_with_retry(map_def)

    def get(self, segment_id, map_id=DEFAULT_MAP_ID,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        map_def = self.entry_def(segment_id=segment_id,
                                 map_id=map_id,
                                 tenant=tenant)
        return self.policy_api.get(map_def, silent=silent)

    def list(self, segment_id,
             tenant=constants.POLICY_INFRA_TENANT):
        map_def = self.entry_def(segment_id=segment_id,
                                 tenant=tenant)
        return self._list(map_def)


class SegmentSecurityProfilesBindingMapApi(SegmentProfilesBindingMapBaseApi):

    @property
    def entry_def(self):
        return core_defs.SegmentSecProfilesBindingMapDef

    def create_or_overwrite(self, name, segment_id,
                            map_id=DEFAULT_MAP_ID,
                            description=IGNORE,
                            segment_security_profile_id=IGNORE,
                            spoofguard_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_def(
            segment_id=segment_id,
            map_id=map_id,
            name=name,
            description=description,
            segment_security_profile_id=segment_security_profile_id,
            spoofguard_profile_id=spoofguard_profile_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def update(self, segment_id,
               map_id=DEFAULT_MAP_ID,
               name=IGNORE,
               description=IGNORE,
               segment_security_profile_id=IGNORE,
               spoofguard_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(
            segment_id=segment_id,
            map_id=map_id,
            name=name,
            description=description,
            segment_security_profile_id=segment_security_profile_id,
            spoofguard_profile_id=spoofguard_profile_id,
            tags=tags,
            tenant=tenant)


class SegmentDiscoveryProfilesBindingMapApi(SegmentProfilesBindingMapBaseApi):

    @property
    def entry_def(self):
        return core_defs.SegmentDiscoveryProfilesBindingMapDef

    def create_or_overwrite(self, name, segment_id,
                            map_id=DEFAULT_MAP_ID,
                            description=IGNORE,
                            ip_discovery_profile_id=IGNORE,
                            mac_discovery_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_def(
            segment_id=segment_id,
            map_id=map_id,
            name=name,
            description=description,
            ip_discovery_profile_id=ip_discovery_profile_id,
            mac_discovery_profile_id=mac_discovery_profile_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def update(self, segment_id,
               map_id=DEFAULT_MAP_ID,
               name=IGNORE,
               description=IGNORE,
               ip_discovery_profile_id=IGNORE,
               mac_discovery_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(
            segment_id=segment_id,
            map_id=map_id,
            name=name,
            description=description,
            ip_discovery_profile_id=ip_discovery_profile_id,
            mac_discovery_profile_id=mac_discovery_profile_id,
            tags=tags,
            tenant=tenant)


class SegmentQosProfilesBindingMapApi(SegmentProfilesBindingMapBaseApi):

    @property
    def entry_def(self):
        return core_defs.SegmentQosProfilesBindingMapDef

    def create_or_overwrite(self, name, segment_id,
                            map_id=DEFAULT_MAP_ID,
                            description=IGNORE,
                            qos_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_def(
            segment_id=segment_id,
            map_id=map_id,
            name=name,
            description=description,
            qos_profile_id=qos_profile_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def update(self, segment_id,
               map_id=DEFAULT_MAP_ID,
               name=IGNORE,
               description=IGNORE,
               qos_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(
            segment_id=segment_id,
            map_id=map_id,
            name=name,
            description=description,
            qos_profile_id=qos_profile_id,
            tags=tags,
            tenant=tenant)


class SegmentPortProfilesBindingMapBaseApi(NsxPolicyResourceBase):

    def delete(self, segment_id, port_id, map_id=DEFAULT_MAP_ID,
               tenant=constants.POLICY_INFRA_TENANT):
        map_def = self.entry_def(segment_id=segment_id,
                                 port_id=port_id,
                                 map_id=map_id,
                                 tenant=tenant)
        self._delete_with_retry(map_def)

    def get(self, segment_id, port_id, map_id=DEFAULT_MAP_ID,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        map_def = self.entry_def(segment_id=segment_id,
                                 port_id=port_id,
                                 map_id=map_id,
                                 tenant=tenant)
        return self.policy_api.get(map_def, silent=silent)

    def list(self, segment_id, port_id,
             tenant=constants.POLICY_INFRA_TENANT):
        map_def = self.entry_def(segment_id=segment_id,
                                 port_id=port_id,
                                 tenant=tenant)
        return self._list(map_def)


class SegmentPortSecurityProfilesBindingMapApi(
    SegmentPortProfilesBindingMapBaseApi):

    @property
    def entry_def(self):
        return core_defs.SegmentPortSecProfilesBindingMapDef

    def create_or_overwrite(self, name, segment_id, port_id,
                            map_id=DEFAULT_MAP_ID,
                            description=IGNORE,
                            segment_security_profile_id=IGNORE,
                            spoofguard_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_def(
            segment_id=segment_id,
            port_id=port_id,
            map_id=map_id,
            name=name,
            description=description,
            segment_security_profile_id=segment_security_profile_id,
            spoofguard_profile_id=spoofguard_profile_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def update(self, segment_id, port_id,
               map_id=DEFAULT_MAP_ID,
               name=IGNORE,
               description=IGNORE,
               segment_security_profile_id=IGNORE,
               spoofguard_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(
            segment_id=segment_id,
            port_id=port_id,
            map_id=map_id,
            name=name,
            description=description,
            segment_security_profile_id=segment_security_profile_id,
            spoofguard_profile_id=spoofguard_profile_id,
            tags=tags,
            tenant=tenant)


class SegmentPortDiscoveryProfilesBindingMapApi(
    SegmentPortProfilesBindingMapBaseApi):

    @property
    def entry_def(self):
        return core_defs.SegmentPortDiscoveryProfilesBindingMapDef

    def create_or_overwrite(self, name, segment_id, port_id,
                            map_id=DEFAULT_MAP_ID,
                            description=IGNORE,
                            mac_discovery_profile_id=IGNORE,
                            ip_discovery_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_def(
            segment_id=segment_id,
            port_id=port_id,
            map_id=map_id,
            name=name,
            description=description,
            mac_discovery_profile_id=mac_discovery_profile_id,
            ip_discovery_profile_id=ip_discovery_profile_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def update(self, segment_id, port_id,
               map_id=DEFAULT_MAP_ID,
               name=IGNORE,
               description=IGNORE,
               mac_discovery_profile_id=IGNORE,
               ip_discovery_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(
            segment_id=segment_id,
            port_id=port_id,
            map_id=map_id,
            name=name,
            description=description,
            mac_discovery_profile_id=mac_discovery_profile_id,
            ip_discovery_profile_id=ip_discovery_profile_id,
            tags=tags,
            tenant=tenant)


class SegmentPortQosProfilesBindingMapApi(
    SegmentPortProfilesBindingMapBaseApi):

    @property
    def entry_def(self):
        return core_defs.SegmentPortQoSProfilesBindingMapDef

    def create_or_overwrite(self, name, segment_id, port_id,
                            map_id=DEFAULT_MAP_ID,
                            description=IGNORE,
                            qos_profile_id=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_def(
            segment_id=segment_id,
            port_id=port_id,
            map_id=map_id,
            name=name,
            description=description,
            qos_profile_id=qos_profile_id,
            tags=tags,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def update(self, segment_id, port_id,
               map_id=DEFAULT_MAP_ID,
               name=IGNORE,
               description=IGNORE,
               qos_profile_id=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(
            segment_id=segment_id,
            port_id=port_id,
            map_id=map_id,
            name=name,
            description=description,
            qos_profile_id=qos_profile_id,
            tags=tags,
            tenant=tenant)


class NsxPolicyTier1SegmentPortApi(NsxPolicyResourceBase):
    """NSX Tier1 Segment Port API """
    @property
    def entry_def(self):
        return core_defs.Tier1SegmentPortDef

    def build_address_binding(self, ip_address, mac_address,
                              vlan_id=None):
        return core_defs.PortAddressBinding(ip_address,
                                            mac_address,
                                            vlan_id)

    def create_or_overwrite(self, name,
                            tier1_id,
                            segment_id,
                            port_id=None,
                            description=IGNORE,
                            address_bindings=IGNORE,
                            attachment_type=IGNORE,
                            vif_id=IGNORE,
                            app_id=IGNORE,
                            context_id=IGNORE,
                            traffic_tag=IGNORE,
                            allocate_addresses=IGNORE,
                            hyperbus_mode=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        port_id = self._init_obj_uuid(port_id)
        port_def = self._init_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  name=name,
                                  description=description,
                                  address_bindings=address_bindings,
                                  attachment_type=attachment_type,
                                  vif_id=vif_id,
                                  app_id=app_id,
                                  context_id=context_id,
                                  traffic_tag=traffic_tag,
                                  allocate_addresses=allocate_addresses,
                                  hyperbus_mode=hyperbus_mode,
                                  tags=tags,
                                  tenant=tenant)
        self._create_or_store(port_def)
        return port_id

    def delete(self, tier1_id, segment_id, port_id,
               tenant=constants.POLICY_INFRA_TENANT):
        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  tenant=tenant)
        self._delete_with_retry(port_def)

    def get(self, tier1_id, segment_id, port_id,
            tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self.policy_api.get(port_def, silent=silent)

    def list(self, tier1_id, segment_id,
             tenant=constants.POLICY_INFRA_TENANT):
        port_def = self.entry_def(segment_id=segment_id, tier1_id=tier1_id,
                                  tenant=tenant)
        return self._list(port_def)

    def update(self, tier1_id, segment_id, port_id,
               name=IGNORE,
               description=IGNORE,
               address_bindings=IGNORE,
               hyperbus_mode=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        self._update(segment_id=segment_id,
                     tier1_id=tier1_id,
                     port_id=port_id,
                     name=name,
                     description=description,
                     address_bindings=address_bindings,
                     hyperbus_mode=hyperbus_mode,
                     tags=tags,
                     tenant=tenant)

    def detach(self, tier1_id, segment_id, port_id,
               tenant=constants.POLICY_INFRA_TENANT):

        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  attachment_type=None,
                                  tenant=tenant)
        self.policy_api.create_or_update(port_def)

    def attach(self, tier1_id, segment_id, port_id,
               attachment_type,
               vif_id,
               allocate_addresses,
               app_id=None,
               context_id=None,
               hyperbus_mode=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  attachment_type=attachment_type,
                                  allocate_addresses=allocate_addresses,
                                  vif_id=vif_id,
                                  app_id=app_id,
                                  context_id=context_id,
                                  hyperbus_mode=hyperbus_mode,
                                  tenant=tenant)

        self.policy_api.create_or_update(port_def)

    def get_realized_state(self, tier1_id, segment_id, port_id,
                           entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self._get_realized_state(port_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, tier1_id, segment_id, port_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self._get_realized_id(port_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, tier1_id, segment_id, port_id,
                             entity_type=None, silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        port_def = self.entry_def(segment_id=segment_id,
                                  tier1_id=tier1_id,
                                  port_id=port_id,
                                  tenant=tenant)
        return self._get_realization_info(port_def, entity_type=entity_type,
                                          silent=silent)

    def wait_until_realized(self, tier1_id, segment_id, port_id,
                            entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        port_def = self.entry_def(segment_id=segment_id, port_id=port_id,
                                  tier1_id=tier1_id, tenant=tenant)
        return self._wait_until_realized(port_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)


# This resource is both for DhcpV4StaticBindingConfig and
# DhcpV6StaticBindingConfig
class SegmentDhcpStaticBindingConfigApi(NsxPolicyResourceBase):
    @property
    def entry_def(self):
        return core_defs.DhcpV4StaticBindingConfig

    def create_or_overwrite(self, name,
                            segment_id,
                            binding_id=None,
                            **kwargs):
        err_msg = (_("This action is not supported. Please call "
                     "create_or_overwrite_v4 or create_or_overwrite_v6"))
        raise exceptions.ManagerError(details=err_msg)

    def create_or_overwrite_v4(self, name,
                               segment_id,
                               binding_id=None,
                               description=IGNORE,
                               gateway_address=IGNORE,
                               host_name=IGNORE,
                               ip_address=IGNORE,
                               lease_time=IGNORE,
                               mac_address=IGNORE,
                               options=IGNORE,
                               tags=IGNORE,
                               tenant=constants.POLICY_INFRA_TENANT):

        binding_id = self._init_obj_uuid(binding_id)
        binding_def = self._init_def(segment_id=segment_id,
                                     binding_id=binding_id,
                                     name=name,
                                     description=description,
                                     gateway_address=gateway_address,
                                     host_name=host_name,
                                     ip_address=ip_address,
                                     lease_time=lease_time,
                                     mac_address=mac_address,
                                     options=options,
                                     tags=tags,
                                     tenant=tenant)
        self._create_or_store(binding_def)
        return binding_id

    def create_or_overwrite_v6(self, name,
                               segment_id,
                               binding_id=None,
                               description=IGNORE,
                               domain_names=IGNORE,
                               dns_nameservers=IGNORE,
                               ip_addresses=IGNORE,
                               sntp_servers=IGNORE,
                               preferred_time=IGNORE,
                               lease_time=IGNORE,
                               mac_address=IGNORE,
                               options=IGNORE,
                               tags=IGNORE,
                               tenant=constants.POLICY_INFRA_TENANT):

        binding_id = self._init_obj_uuid(binding_id)
        args = self._get_user_args(segment_id=segment_id,
                                   binding_id=binding_id,
                                   name=name,
                                   description=description,
                                   domain_names=domain_names,
                                   dns_nameservers=dns_nameservers,
                                   ip_addresses=ip_addresses,
                                   sntp_servers=sntp_servers,
                                   preferred_time=preferred_time,
                                   lease_time=lease_time,
                                   mac_address=mac_address,
                                   options=options,
                                   tags=tags,
                                   tenant=tenant)
        binding_def = core_defs.DhcpV6StaticBindingConfig(**args)
        self._create_or_store(binding_def)
        return binding_id

    def delete(self, segment_id, binding_id,
               tenant=constants.POLICY_INFRA_TENANT):
        binding_def = self.entry_def(segment_id=segment_id,
                                     binding_id=binding_id,
                                     tenant=tenant)
        self._delete_with_retry(binding_def)

    def get(self, segment_id, binding_id,
            tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        binding_def = self.entry_def(segment_id=segment_id,
                                     binding_id=binding_id,
                                     tenant=tenant)
        return self.policy_api.get(binding_def, silent=silent)

    def list(self, segment_id, tenant=constants.POLICY_INFRA_TENANT):
        binding_def = self.entry_def(segment_id=segment_id, tenant=tenant)
        return self._list(binding_def)

    def update(self, segment_id, binding_id, **kwargs):
        err_msg = (_("This action is currently not supported"))
        raise exceptions.ManagerError(details=err_msg)


class NsxPolicyIpBlockApi(NsxPolicyResourceBase):
    """NSX Policy IP Block API"""
    @property
    def entry_def(self):
        return core_defs.IpBlockDef

    def create_or_overwrite(self, name,
                            ip_block_id=None,
                            description=IGNORE,
                            cidr=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        ip_block_id = self._init_obj_uuid(ip_block_id)
        ip_block_def = self._init_def(ip_block_id=ip_block_id,
                                      name=name,
                                      description=description,
                                      cidr=cidr,
                                      tags=tags,
                                      tenant=tenant)
        self._create_or_store(ip_block_def)
        return ip_block_id

    def delete(self, ip_block_id, tenant=constants.POLICY_INFRA_TENANT):
        ip_block_def = self.entry_def(ip_block_id=ip_block_id,
                                      tenant=tenant)
        self._delete_with_retry(ip_block_def)

    def get(self, ip_block_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        ip_block_def = self.entry_def(ip_block_id=ip_block_id,
                                      tenant=tenant)
        return self.policy_api.get(ip_block_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        ip_block_def = self.entry_def(tenant=tenant)
        return self._list(ip_block_def)

    def update(self, ip_block_id, name=IGNORE, description=IGNORE,
               cidr=IGNORE, tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(ip_block_id=ip_block_id,
                     name=name,
                     description=description,
                     cidr=cidr,
                     tags=tags,
                     tenant=tenant)


class NsxPolicyIpPoolApi(NsxPolicyResourceBase):
    """NSX Policy IP Pool API"""
    @property
    def entry_def(self):
        return core_defs.IpPoolDef

    def create_or_overwrite(self, name,
                            ip_pool_id=None,
                            description=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        ip_pool_id = self._init_obj_uuid(ip_pool_id)
        ip_pool_def = self._init_def(ip_pool_id=ip_pool_id,
                                     name=name,
                                     description=description,
                                     tags=tags,
                                     tenant=tenant)
        self._create_or_store(ip_pool_def)
        return ip_pool_id

    def delete(self, ip_pool_id, tenant=constants.POLICY_INFRA_TENANT):
        ip_pool_def = self.entry_def(ip_pool_id=ip_pool_id,
                                     tenant=tenant)
        self._delete_or_store(ip_pool_def)

    def get(self, ip_pool_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        ip_pool_def = self.entry_def(ip_pool_id=ip_pool_id,
                                     tenant=tenant)
        return self.policy_api.get(ip_pool_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        ip_pool_def = self.entry_def(tenant=tenant)
        return self._list(ip_pool_def)

    def update(self, ip_pool_id, name=IGNORE, description=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(ip_pool_id=ip_pool_id,
                     name=name,
                     description=description,
                     tags=tags,
                     tenant=tenant)

    def allocate_ip(self, ip_pool_id, ip_allocation_id=None, ip_address=IGNORE,
                    name=IGNORE, description=IGNORE, tags=IGNORE,
                    tenant=constants.POLICY_INFRA_TENANT):
        # If ip_address is not set, a random IP will be allocated
        # from the pool.
        ip_allocation_id = self._init_obj_uuid(ip_allocation_id)

        args = self._get_user_args(
            ip_pool_id=ip_pool_id,
            ip_allocation_id=ip_allocation_id,
            allocation_ip=ip_address,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant)

        ip_allocation_def = core_defs.IpPoolAllocationDef(**args)
        self._create_or_store(ip_allocation_def)

    def release_ip(self, ip_pool_id, ip_allocation_id,
                   tenant=constants.POLICY_INFRA_TENANT):
        ip_allocation_def = core_defs.IpPoolAllocationDef(
            ip_allocation_id=ip_allocation_id,
            ip_pool_id=ip_pool_id,
            tenant=tenant)
        self._delete_with_retry(ip_allocation_def)

    def list_allocations(self, ip_pool_id,
                         tenant=constants.POLICY_INFRA_TENANT):
        ip_allocation_def = core_defs.IpPoolAllocationDef(
            ip_pool_id=ip_pool_id,
            tenant=tenant)
        return self._list(ip_allocation_def)

    def get_allocation(self, ip_pool_id, ip_allocation_id,
                       tenant=constants.POLICY_INFRA_TENANT):
        ip_allocation_def = core_defs.IpPoolAllocationDef(
            ip_pool_id=ip_pool_id,
            ip_allocation_id=ip_allocation_id,
            tenant=tenant)
        return self.policy_api.get(ip_allocation_def)

    def allocate_block_subnet(self, ip_pool_id, ip_block_id, size,
                              ip_subnet_id=None, auto_assign_gateway=IGNORE,
                              name=IGNORE, description=IGNORE, tags=IGNORE,
                              tenant=constants.POLICY_INFRA_TENANT,
                              start_ip=IGNORE):
        ip_subnet_id = self._init_obj_uuid(ip_subnet_id)
        args = self._get_user_args(
            ip_pool_id=ip_pool_id,
            ip_block_id=ip_block_id,
            ip_subnet_id=ip_subnet_id,
            size=size,
            auto_assign_gateway=auto_assign_gateway,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant,
            start_ip=start_ip)

        ip_subnet_def = core_defs.IpPoolBlockSubnetDef(
            nsx_version=self.version, **args)
        self._create_or_store(ip_subnet_def)

    def release_block_subnet(self, ip_pool_id, ip_subnet_id,
                             tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_def = core_defs.IpPoolBlockSubnetDef(
            ip_subnet_id=ip_subnet_id,
            ip_pool_id=ip_pool_id,
            tenant=tenant)
        self._delete_with_retry(ip_subnet_def)

    def list_block_subnets(self, ip_pool_id,
                           tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_def = core_defs.IpPoolBlockSubnetDef(
            ip_pool_id=ip_pool_id,
            tenant=tenant)
        subnets = self._list(ip_subnet_def)
        block_subnets = []
        for subnet in subnets:
            if subnet['resource_type'] == ip_subnet_def.resource_type():
                block_subnets.append(subnet)
        return block_subnets

    def get_ip_block_subnet(self, ip_pool_id, ip_subnet_id,
                            tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_def = core_defs.IpPoolBlockSubnetDef(
            ip_pool_id=ip_pool_id,
            ip_subnet_id=ip_subnet_id,
            tenant=tenant)
        return self.policy_api.get(ip_subnet_def)

    def get_ip_block_subnet_cidr(self, ip_pool_id, ip_subnet_id,
                                 entity_type=None,
                                 tenant=constants.POLICY_INFRA_TENANT,
                                 wait=False, sleep=None,
                                 max_attempts=None):
        # Retrieve the allocated Subnet CIDR for Subnet ID
        # Return None in case the CIDR is not yet allocated
        realized_info = self.get_ip_subnet_realization_info(
            ip_pool_id, ip_subnet_id, entity_type, tenant, wait,
            sleep, max_attempts)
        # Returns a list of CIDRs. In case a single value is expected,
        # caller must extract the first index to retrieve the CIDR value
        return self._get_extended_attr_from_realized_info(
            realized_info, requested_attr='cidr')

    def create_or_update_static_subnet(self, ip_pool_id, cidr,
                                       allocation_ranges, ip_subnet_id=None,
                                       name=IGNORE, description=IGNORE,
                                       gateway_ip=IGNORE, tags=IGNORE,
                                       tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_id = self._init_obj_uuid(ip_subnet_id)
        args = self._get_user_args(
            ip_pool_id=ip_pool_id,
            ip_subnet_id=ip_subnet_id,
            cidr=cidr,
            allocation_ranges=allocation_ranges,
            name=name,
            description=description,
            tags=tags,
            tenant=tenant)

        ip_subnet_def = core_defs.IpPoolStaticSubnetDef(**args)
        self._create_or_store(ip_subnet_def)

    def release_static_subnet(self, ip_pool_id, ip_subnet_id,
                              tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_def = core_defs.IpPoolStaticSubnetDef(
            ip_subnet_id=ip_subnet_id,
            ip_pool_id=ip_pool_id,
            tenant=tenant)
        self._delete_with_retry(ip_subnet_def)

    def list_static_subnets(self, ip_pool_id,
                            tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_def = core_defs.IpPoolStaticSubnetDef(
            ip_pool_id=ip_pool_id,
            tenant=tenant)
        subnets = self._list(ip_subnet_def)
        static_subnets = []
        for subnet in subnets:
            if subnet['resource_type'] == ip_subnet_def.resource_type():
                static_subnets.append(subnet)
        return static_subnets

    def get_static_subnet(self, ip_pool_id, ip_subnet_id,
                          tenant=constants.POLICY_INFRA_TENANT):
        ip_subnet_def = core_defs.IpPoolStaticSubnetDef(
            ip_pool_id=ip_pool_id,
            ip_subnet_id=ip_subnet_id,
            tenant=tenant)
        return self.policy_api.get(ip_subnet_def)

    def get_realization_info(self, ip_pool_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        ip_pool_def = self.entry_def(ip_pool_id=ip_pool_id, tenant=tenant)
        return self._get_realization_info(ip_pool_def, entity_type=entity_type,
                                          silent=silent)

    def get_ip_subnet_realization_info(
            self, ip_pool_id, ip_subnet_id,
            entity_type=None,
            tenant=constants.POLICY_INFRA_TENANT,
            wait=False, sleep=None,
            max_attempts=None,
            subnet_type=constants.IPPOOL_BLOCK_SUBNET, all_results=False):
        if subnet_type == constants.IPPOOL_BLOCK_SUBNET:
            ip_subnet_def = core_defs.IpPoolBlockSubnetDef(
                ip_pool_id=ip_pool_id,
                ip_subnet_id=ip_subnet_id,
                tenant=tenant)
        else:
            ip_subnet_def = core_defs.IpPoolStaticSubnetDef(
                ip_pool_id=ip_pool_id,
                ip_subnet_id=ip_subnet_id,
                tenant=tenant)
        if wait:
            return self._wait_until_realized(
                ip_subnet_def, entity_type=entity_type,
                sleep=sleep, max_attempts=max_attempts,
                all_results=all_results)
        return self._get_realization_info(
            ip_subnet_def, entity_type=entity_type, all_results=all_results)

    def get_ip_alloc_realization_info(self, ip_pool_id, ip_allocation_id,
                                      entity_type=None,
                                      tenant=constants.POLICY_INFRA_TENANT,
                                      wait=False, sleep=None,
                                      max_attempts=None):
        ip_allocation_def = core_defs.IpPoolAllocationDef(
            ip_pool_id=ip_pool_id,
            ip_allocation_id=ip_allocation_id,
            tenant=tenant)
        if wait:
            return self._wait_until_realized(
                ip_allocation_def, entity_type=entity_type,
                sleep=sleep, max_attempts=max_attempts)
        return self._get_realization_info(ip_allocation_def,
                                          entity_type=entity_type)

    def get_realized_allocated_ip(self, ip_pool_id, ip_allocation_id,
                                  entity_type=None,
                                  tenant=constants.POLICY_INFRA_TENANT,
                                  wait=False, sleep=None,
                                  max_attempts=None):
        # Retrieve the allocated IpAddress for allocation ID
        # Return None in case the IP is not yet allocated
        realized_info = self.get_ip_alloc_realization_info(
            ip_pool_id, ip_allocation_id, entity_type, tenant, wait,
            sleep, max_attempts)
        if realized_info:
            try:
                return realized_info['extended_attributes'][0].get(
                    'values')[0]
            except IndexError:
                return

    def wait_until_realized(self, ip_pool_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        ip_pool_def = self.entry_def(ip_pool_id=ip_pool_id, tenant=tenant)
        return self._wait_until_realized(ip_pool_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)


class NsxPolicySecurityPolicyBaseApi(NsxPolicyResourceBase):

    def _get_last_seq_num(self, domain_id, map_id,
                          tenant=constants.POLICY_INFRA_TENANT):
        # get the current entries, and choose the next unused sequence number
        # between the entries under the same communication map
        try:
            com_map = self.get(domain_id, map_id, tenant=tenant)
            com_entries = com_map.get('rules')
        except exceptions.ResourceNotFound:
            return -1
        if not com_entries:
            return 0
        seq_nums = [int(cm['sequence_number']) for cm in com_entries]
        seq_nums.sort()
        return seq_nums[-1]

    def _get_seq_num(self, last_sequence):
        if last_sequence < 0:
            return 1
        return last_sequence + 1

    def create_or_overwrite(self, name, domain_id, map_id=None,
                            description=IGNORE,
                            category=constants.CATEGORY_APPLICATION,
                            sequence_number=None, service_ids=IGNORE,
                            action=constants.ACTION_ALLOW,
                            scope=IGNORE,
                            source_groups=IGNORE, dest_groups=IGNORE,
                            direction=nsx_constants.IN_OUT,
                            logged=IGNORE, tags=IGNORE,
                            map_sequence_number=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        """Create CommunicationMap & Entry.

        source_groups/dest_groups should be a list of group ids belonging
        to the domain.
        NOTE: In multi-connection environment, it is recommended to execute
        this call under lock to prevent race condition where two entries
        end up with same sequence number.
        """
        last_sequence = -1
        if map_id:
            if not sequence_number:
                # get the next available sequence number
                last_sequence = self._get_last_seq_num(domain_id, map_id,
                                                       tenant=tenant)
        else:
            map_id = self._init_obj_uuid(map_id)

        if not sequence_number:
            sequence_number = self._get_seq_num(last_sequence)

        # Build the communication entry. Since we currently support only one
        # it will have the same id as its parent
        entry_def = self._init_def(
            domain_id=domain_id,
            map_id=map_id,
            entry_id=self.SINGLE_ENTRY_ID,
            name=name,
            description=description,
            sequence_number=sequence_number,
            source_groups=source_groups,
            dest_groups=dest_groups,
            service_ids=service_ids,
            action=action,
            scope=scope,
            direction=direction,
            logged=logged,
            tenant=tenant)

        map_def = self._init_parent_def(
            domain_id=domain_id, map_id=map_id,
            tenant=tenant, name=name, description=description,
            category=category, tags=tags,
            map_sequence_number=map_sequence_number)

        self._create_or_store(map_def, entry_def)
        return map_id

    def create_or_overwrite_map_only(
        self, name, domain_id, map_id=None, description=IGNORE,
        category=constants.CATEGORY_APPLICATION,
        tags=IGNORE, map_sequence_number=IGNORE,
        tenant=constants.POLICY_INFRA_TENANT):
        """Create or update a CommunicationMap

        Create a communication map without any entries, or update the
        communication map itself, leaving the entries unchanged.
        """
        map_id = self._init_obj_uuid(map_id)
        map_def = self._init_parent_def(
            domain_id=domain_id, map_id=map_id,
            tenant=tenant, name=name, description=description,
            category=category, tags=tags,
            map_sequence_number=map_sequence_number)

        self._create_or_store(map_def)
        return map_id

    def build_entry(self, name, domain_id, map_id, entry_id=None,
                    description=None,
                    sequence_number=None, service_ids=None,
                    action=constants.ACTION_ALLOW,
                    scope=None,
                    source_groups=None, dest_groups=None,
                    direction=nsx_constants.IN_OUT, logged=False, tag=None,
                    ip_protocol=nsx_constants.IPV4_IPV6,
                    service_entries=IGNORE,
                    tenant=constants.POLICY_INFRA_TENANT,
                    plain_groups=False):
        """Get the definition of a single map entry.

        plain_groups should be True if source_groups/dest_groups is a list
        of group paths and IP addresses. IP address support from NSX 3.0.0.
        """
        if (version.LooseVersion(self.version) <
            version.LooseVersion(nsx_constants.NSX_VERSION_3_0_0) and
            plain_groups):
            err_msg = _("plain_groups support is from NSX 3.0.0")
            raise exceptions.NsxLibInvalidInput(error_message=err_msg)

        entry_id = self._init_obj_uuid(entry_id)
        return self._init_def(domain_id=domain_id,
                              map_id=map_id,
                              entry_id=entry_id,
                              name=name,
                              description=description,
                              sequence_number=sequence_number,
                              source_groups=source_groups,
                              dest_groups=dest_groups,
                              service_ids=service_ids,
                              action=action,
                              scope=scope,
                              direction=direction,
                              ip_protocol=ip_protocol,
                              logged=logged,
                              tag=tag,
                              service_entries=service_entries,
                              tenant=tenant,
                              plain_groups=plain_groups)

    def create_with_entries(
        self, name, domain_id, map_id=None,
        description=IGNORE,
        category=constants.CATEGORY_APPLICATION,
        entries=None, tags=IGNORE, map_sequence_number=IGNORE,
        tenant=constants.POLICY_INFRA_TENANT):
        """Create CommunicationMap with entries"""

        map_id = self._init_obj_uuid(map_id)

        map_def = self._init_parent_def(
            domain_id=domain_id, map_id=map_id,
            tenant=tenant, name=name, description=description,
            category=category, tags=tags,
            map_sequence_number=map_sequence_number)

        # in case the same object was just deleted, create may need to
        # be retried
        @utils.retry_upon_exception(
            exceptions.NsxPendingDelete,
            delay=self.nsxlib_config.realization_wait_sec,
            max_attempts=self.nsxlib_config.realization_max_attempts)
        def _do_create_with_retry():
            self._create_or_store(map_def, entries)

        _do_create_with_retry()
        return map_id

    def create_entry(self, name, domain_id, map_id, entry_id=None,
                     description=None, sequence_number=None, service_ids=None,
                     action=constants.ACTION_ALLOW,
                     source_groups=None, dest_groups=None,
                     scope=None, tags=IGNORE,
                     ip_protocol=nsx_constants.IPV4_IPV6,
                     direction=nsx_constants.IN_OUT,
                     logged=False, tag=None,
                     service_entries=IGNORE,
                     tenant=constants.POLICY_INFRA_TENANT,
                     plain_groups=False):
        """Create CommunicationMap Entry.

        source_groups/dest_groups should be a list of group ids belonging
        to the domain.

        plain_groups should be True if source_groups/dest_groups is a list
        of group paths and IP addresses. IP address support from NSX 3.0.0.
        """
        if (version.LooseVersion(self.version) <
            version.LooseVersion(nsx_constants.NSX_VERSION_3_0_0) and
            plain_groups):
            err_msg = _("plain_groups support is from NSX 3.0.0")
            raise exceptions.NsxLibInvalidInput(error_message=err_msg)

        # get the next available sequence number
        if not sequence_number:
            last_sequence = self._get_last_seq_num(domain_id, map_id,
                                                   tenant=tenant)
            sequence_number = self._get_seq_num(last_sequence)
        entry_id = self._init_obj_uuid(entry_id)

        # Build the communication entry
        entry_def = self._init_def(domain_id=domain_id,
                                   map_id=map_id,
                                   entry_id=entry_id,
                                   name=name,
                                   description=description,
                                   sequence_number=sequence_number,
                                   source_groups=source_groups,
                                   dest_groups=dest_groups,
                                   service_ids=service_ids,
                                   action=action,
                                   scope=scope,
                                   ip_protocol=ip_protocol,
                                   direction=direction,
                                   logged=logged,
                                   tag=tag,
                                   tags=tags,
                                   service_entries=service_entries,
                                   tenant=tenant,
                                   plain_groups=plain_groups)

        self._create_or_store(entry_def)
        return entry_id

    def create_entry_from_def(self, entry_def):
        """Create CommunicationMap Entry from a predefined entry def"""
        self._create_or_store(entry_def)

    def delete(self, domain_id, map_id,
               tenant=constants.POLICY_INFRA_TENANT):
        map_def = self._init_parent_def(
            domain_id=domain_id,
            map_id=map_id,
            tenant=tenant)
        self._delete_with_retry(map_def)

    def delete_entry(self, domain_id, map_id, entry_id,
                     tenant=constants.POLICY_INFRA_TENANT):
        entry_def = self.entry_def(
            domain_id=domain_id,
            map_id=map_id,
            entry_id=entry_id,
            tenant=tenant)
        self._delete_with_retry(entry_def)

    def get(self, domain_id, map_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        map_def = self.parent_entry_def(
            domain_id=domain_id,
            map_id=map_id,
            tenant=tenant)
        return self.policy_api.get(map_def, silent=silent)

    def get_entry(self, domain_id, map_id, entry_id,
                  tenant=constants.POLICY_INFRA_TENANT, silent=False):
        entry_def = self.entry_def(
            domain_id=domain_id,
            map_id=map_id,
            entry_id=entry_id,
            tenant=tenant)
        return self.policy_api.get(entry_def, silent=silent)

    def get_by_name(self, domain_id, name,
                    tenant=constants.POLICY_INFRA_TENANT):
        """Return first communication map entry matched by name"""
        return super(NsxPolicySecurityPolicyBaseApi, self).get_by_name(
            name, domain_id, tenant=tenant)

    def list(self, domain_id,
             tenant=constants.POLICY_INFRA_TENANT):
        """List all the map entries of a specific domain."""
        map_def = self.parent_entry_def(
            domain_id=domain_id,
            tenant=tenant)
        return self._list(map_def)

    def update(self, domain_id, map_id,
               name=IGNORE, description=IGNORE,
               sequence_number=IGNORE, service_ids=IGNORE,
               action=IGNORE,
               source_groups=IGNORE, dest_groups=IGNORE,
               direction=IGNORE, logged=IGNORE, tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        # Note(asarfaty): Category is mandatory in update calls for now
        # although it cannot change. Getting it from the NSX
        orig_entry = self.get(domain_id, map_id, tenant=tenant)
        category = orig_entry.get('category')
        parent_def = self._init_parent_def(
            domain_id=domain_id,
            map_id=map_id,
            name=name,
            description=description,
            category=category,
            tags=tags,
            tenant=tenant)

        if self._any_arg_set(sequence_number, service_ids,
                             action, source_groups, dest_groups,
                             direction, logged):
            # Update the entry only if relevant attributes were changed
            entry_def = self._get_and_update_def(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=self.SINGLE_ENTRY_ID,
                service_ids=service_ids,
                source_groups=source_groups,
                dest_groups=dest_groups,
                sequence_number=sequence_number,
                action=action,
                direction=direction,
                logged=logged,
                tenant=tenant)

            self.policy_api.create_with_parent(parent_def, entry_def)
        else:
            self.policy_api.create_or_update(parent_def)

    def update_entry(self, domain_id, map_id, entry_id,
                     name=IGNORE, description=IGNORE,
                     sequence_number=IGNORE, service_ids=IGNORE,
                     action=IGNORE, source_groups=IGNORE, dest_groups=IGNORE,
                     scope=IGNORE, ip_protocol=IGNORE,
                     direction=IGNORE, logged=IGNORE, tags=IGNORE, tag=IGNORE,
                     service_entries=IGNORE,
                     tenant=constants.POLICY_INFRA_TENANT):
        if self._any_arg_set(name, description, sequence_number, service_ids,
                             action, source_groups, dest_groups, scope,
                             ip_protocol, direction, logged, tags):
            entry_def = self._get_and_update_def(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=entry_id,
                name=name,
                description=description,
                sequence_number=sequence_number,
                service_ids=service_ids,
                action=action,
                source_groups=source_groups,
                dest_groups=dest_groups,
                scope=scope,
                ip_protocol=ip_protocol,
                direction=direction,
                logged=logged,
                tags=tags,
                tag=tag,
                service_entries=service_entries,
                tenant=tenant)
            self.policy_api.create_or_update(entry_def)

    def update_entries(self, domain_id, map_id, entries,
                       category=constants.CATEGORY_APPLICATION,
                       use_child_rules=True,
                       tenant=constants.POLICY_INFRA_TENANT):
        self.update_with_entries(domain_id, map_id, entries, category=category,
                                 use_child_rules=use_child_rules,
                                 tenant=tenant)

    def update_with_entries(self, domain_id, map_id, entries=IGNORE,
                            name=IGNORE, description=IGNORE,
                            category=constants.CATEGORY_APPLICATION,
                            tags=IGNORE, map_sequence_number=IGNORE,
                            use_child_rules=True,
                            tenant=constants.POLICY_INFRA_TENANT):
        map_def = self._init_parent_def(
            domain_id=domain_id, map_id=map_id,
            tenant=tenant, name=name, description=description,
            category=category, tags=tags,
            map_sequence_number=map_sequence_number)
        map_path = map_def.get_resource_path()

        def _overwrite_entries(old_entries, new_entries, transaction):
            # Replace old entries with new entries, but copy additional
            # attributes from old entries for those kept in new entries
            # and marked the unwanted ones in the old entries as deleted
            # if it is in the transaction call.
            old_rules = {entry["id"]: entry for entry in old_entries}
            replaced_entries = []
            for entry in new_entries:
                rule_id = entry.get_id()
                new_rule = entry.get_obj_dict()
                old_rule = old_rules.get(rule_id)
                if old_rule:
                    old_rules.pop(rule_id)
                    for key, value in old_rule.items():
                        if key not in new_rule:
                            new_rule[key] = value
                replaced_entries.append(
                    self.entry_def.adapt_from_rule_dict(
                        new_rule, domain_id, map_id))

            if transaction:
                replaced_entries.extend(
                    _mark_delete_entries(old_rules.values()))
            return replaced_entries

        def _mark_delete_entries(delete_rule_dicts):
            delete_entries = []
            for delete_rule_dict in delete_rule_dicts:
                delete_entry = self.entry_def.adapt_from_rule_dict(
                    delete_rule_dict, domain_id, map_id)
                delete_entry.set_delete()
                delete_entries.append(delete_entry)
            return delete_entries

        @utils.retry_upon_exception(
            exceptions.StaleRevision,
            max_attempts=self.policy_api.client.max_attempts)
        def _update():
            transaction = trans.NsxPolicyTransaction.get_current()
            # Get the current data of communication map & its entries
            comm_map = self.policy_api.get(map_def)
            replaced_entries = None
            ignore_entries = (entries == IGNORE)
            if not ignore_entries:
                replaced_entries = _overwrite_entries(comm_map['rules'],
                                                      entries, transaction)
                comm_map.pop('rules')
            map_def.set_obj_dict(comm_map)
            # Update the entire map at the NSX
            if transaction:
                if use_child_rules:
                    self._create_or_store(map_def, replaced_entries)
                else:
                    if not ignore_entries:
                        # Add the rules under the map and not as ChildRules for
                        # improved performance on the NSX side
                        comm_map['rules'] = [rule.get_obj_dict() for rule in
                                             replaced_entries]
                        map_def.set_obj_dict(comm_map)
                    self._create_or_store(map_def)
            else:
                body = map_def.get_obj_dict()
                if not ignore_entries:
                    body['rules'] = [rule.get_obj_dict() for rule in
                                     replaced_entries]
                self.policy_api.client.update(map_path, body)

        _update()

    def update_entries_logged(self, domain_id, map_id, logged,
                              tenant=constants.POLICY_INFRA_TENANT):
        """Update all communication map entries logged flags"""
        map_def = self.parent_entry_def(
            domain_id=domain_id,
            map_id=map_id,
            tenant=tenant)
        map_path = map_def.get_resource_path()

        @utils.retry_upon_exception(
            exceptions.StaleRevision,
            max_attempts=self.policy_api.client.max_attempts)
        def _update():
            # Get the current data of communication map & its' entries
            comm_map = self.policy_api.get(map_def)
            # Update the field in all the entries
            if comm_map.get('rules'):
                for comm_entry in comm_map['rules']:
                    comm_entry['logged'] = logged
            # Update the entire map at the NSX
            self.policy_api.client.update(map_path, comm_map)

        _update()

    def get_realized_state(self, domain_id, map_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        map_def = self.parent_entry_def(map_id=map_id,
                                        domain_id=domain_id,
                                        tenant=tenant)
        return self._get_realized_state(map_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realized_id(self, domain_id, map_id, entity_type=None,
                        tenant=constants.POLICY_INFRA_TENANT,
                        realization_info=None):
        map_def = self.parent_entry_def(map_id=map_id,
                                        domain_id=domain_id,
                                        tenant=tenant)
        return self._get_realized_id(map_def, entity_type=entity_type,
                                     realization_info=realization_info)

    def get_realization_info(self, domain_id, map_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT):
        map_def = self.parent_entry_def(map_id=map_id,
                                        domain_id=domain_id,
                                        tenant=tenant)
        return self._get_realization_info(map_def, entity_type=entity_type,
                                          silent=silent)

    def wait_until_realized(self, domain_id, map_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        map_def = self.parent_entry_def(map_id=map_id,
                                        domain_id=domain_id,
                                        tenant=tenant)
        return self._wait_until_realized(map_def, entity_type=entity_type,
                                         sleep=sleep,
                                         max_attempts=max_attempts)

    def wait_until_state_sucessful(self, domain_id, map_id,
                                   tenant=constants.POLICY_INFRA_TENANT,
                                   sleep=None, max_attempts=None,
                                   with_refresh=False):
        map_def = self.parent_entry_def(map_id=map_id,
                                        domain_id=domain_id,
                                        tenant=tenant)
        self._wait_until_state_successful(map_def, sleep=sleep,
                                          max_attempts=max_attempts,
                                          with_refresh=with_refresh)


class NsxPolicyCommunicationMapApi(NsxPolicySecurityPolicyBaseApi):
    """NSX Policy CommunicationMap (Under a Domain). AKA Security"""
    @property
    def entry_def(self):
        return core_defs.CommunicationMapEntryDef

    @property
    def parent_entry_def(self):
        return core_defs.CommunicationMapDef


class NsxPolicyGatewayPolicyApi(NsxPolicySecurityPolicyBaseApi):
    """NSX Policy Gateway policy (Edge firewall)"""
    @property
    def entry_def(self):
        return core_defs.GatewayPolicyRuleDef

    @property
    def parent_entry_def(self):
        return core_defs.GatewayPolicyDef


class NsxPolicyEnforcementPointApi(NsxPolicyResourceBase):
    """NSX Policy Enforcement Point."""

    @property
    def entry_def(self):
        return core_defs.EnforcementPointDef

    def create_or_overwrite(self, name, ep_id=None, description=IGNORE,
                            ip_address=IGNORE, username=IGNORE,
                            password=IGNORE, thumbprint=IGNORE,
                            edge_cluster_id=IGNORE,
                            transport_zone_id=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        if not ip_address or not username or password is None:
            err_msg = (_("Cannot create an enforcement point without "
                         "ip_address, username and password"))
            raise exceptions.ManagerError(details=err_msg)
        ep_id = self._init_obj_uuid(ep_id)
        ep_def = self._init_def(ep_id=ep_id,
                                name=name,
                                description=description,
                                ip_address=ip_address,
                                username=username,
                                password=password,
                                thumbprint=thumbprint,
                                edge_cluster_id=edge_cluster_id,
                                transport_zone_id=transport_zone_id,
                                tenant=tenant)
        self._create_or_store(ep_def)
        return ep_id

    def delete(self, ep_id,
               tenant=constants.POLICY_INFRA_TENANT):
        ep_def = core_defs.EnforcementPointDef(
            ep_id=ep_id, tenant=tenant)
        self._delete_with_retry(ep_def)

    def get(self, ep_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        ep_def = core_defs.EnforcementPointDef(
            ep_id=ep_id, tenant=tenant)
        return self.policy_api.get(ep_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        ep_def = core_defs.EnforcementPointDef(tenant=tenant)
        return self._list(ep_def)

    def update(self, ep_id, name=IGNORE, description=IGNORE,
               ip_address=IGNORE, username=IGNORE,
               password=IGNORE, thumbprint=IGNORE,
               edge_cluster_id=IGNORE, transport_zone_id=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        """Update the enforcement point.

        username & password must be defined
        """
        if not username or password is None:
            # username/password must be provided
            err_msg = (_("Cannot update an enforcement point without "
                         "username and password"))
            raise exceptions.ManagerError(details=err_msg)

        # Get the original body because ip & thumbprint are mandatory
        ep_def = self._get_and_update_def(ep_id=ep_id,
                                          name=name,
                                          description=description,
                                          ip_address=ip_address,
                                          username=username,
                                          password=password,
                                          edge_cluster_id=edge_cluster_id,
                                          transport_zone_id=transport_zone_id,
                                          thumbprint=thumbprint,
                                          tenant=tenant)

        self.policy_api.create_or_update(ep_def)

    def get_realized_state(self, ep_id, entity_type=None,
                           tenant=constants.POLICY_INFRA_TENANT,
                           realization_info=None):
        ep_def = core_defs.EnforcementPointDef(ep_id=ep_id, tenant=tenant)
        return self._get_realized_state(ep_def, entity_type=entity_type,
                                        realization_info=realization_info)

    def get_realization_info(self, ep_id, entity_type=None,
                             silent=False,
                             tenant=constants.POLICY_INFRA_TENANT,
                             realization_info=None):
        ep_def = core_defs.EnforcementPointDef(ep_id=ep_id, tenant=tenant)
        return self._get_realization_info(ep_def, entity_type=entity_type,
                                          silent=silent,
                                          realization_info=realization_info)

    def reload(self, ep_id, tenant=constants.POLICY_INFRA_TENANT):
        # Use post command to reload the enforcement point
        ep_def = core_defs.EnforcementPointDef(ep_id=ep_id, tenant=tenant)
        path = "%s?action=reload" % ep_def.get_resource_path()
        self.policy_api.client.create(path)


class NsxPolicyTransportZoneApi(NsxPolicyResourceBase):

    TZ_TYPE_OVERLAY = 'OVERLAY_STANDARD'
    TZ_TYPE_ENS = 'OVERLAY_ENS'
    TZ_TYPE_VLAN = 'VLAN_BACKED'

    @property
    def entry_def(self):
        return core_defs.TransportZoneDef

    def get(self, tz_id, ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        tz_def = core_defs.TransportZoneDef(
            ep_id=ep_id, tz_id=tz_id, tenant=tenant)
        return self.policy_api.get(tz_def, silent=silent)

    def get_tz_type(self, tz_id,
                    ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                    tenant=constants.POLICY_INFRA_TENANT):
        tz = self.get(tz_id, ep_id=ep_id, tenant=tenant)
        return tz.get('tz_type')

    def get_transport_type(self, tz_id,
                           ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                           tenant=constants.POLICY_INFRA_TENANT):
        """This api is consistent with the nsx manager resource api"""
        tz_type = self.get_tz_type(tz_id, ep_id=ep_id, tenant=tenant)
        if tz_type == self.TZ_TYPE_VLAN:
            return nsx_constants.TRANSPORT_TYPE_VLAN
        else:
            return nsx_constants.TRANSPORT_TYPE_OVERLAY

    def get_host_switch_mode(self, tz_id,
                             ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                             tenant=constants.POLICY_INFRA_TENANT):
        """This api is consistent with the nsx manager resource api"""
        tz_type = self.get_tz_type(tz_id, ep_id=ep_id, tenant=tenant)
        if tz_type == self.TZ_TYPE_ENS:
            return nsx_constants.HOST_SWITCH_MODE_ENS
        else:
            return nsx_constants.HOST_SWITCH_MODE_STANDARD

    def list(self, ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
             tenant=constants.POLICY_INFRA_TENANT):
        tz_def = core_defs.TransportZoneDef(ep_id=ep_id, tenant=tenant)
        return self._list(tz_def)

    def get_by_name(self, name,
                    ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                    tenant=constants.POLICY_INFRA_TENANT):
        """Return first group matched by name"""
        return super(NsxPolicyTransportZoneApi, self).get_by_name(
            name, ep_id, tenant=tenant)

    def create_or_overwrite(self, name, tz_id=None,
                            ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                            tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def update(self, tz_id,
               ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def delete(self, tz_id,
               ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)


class NsxPolicyEdgeClusterApi(NsxPolicyResourceBase):
    @property
    def entry_def(self):
        return core_defs.EdgeClusterDef

    def get(self, ec_id, ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        ec_def = core_defs.EdgeClusterDef(
            ep_id=ep_id, ec_id=ec_id, tenant=tenant)
        return self.policy_api.get(ec_def, silent=silent)

    def list(self, ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
             tenant=constants.POLICY_INFRA_TENANT):
        ec_def = core_defs.EdgeClusterDef(ep_id=ep_id, tenant=tenant)
        return self._list(ec_def)

    def get_by_name(self, name,
                    ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                    tenant=constants.POLICY_INFRA_TENANT):
        """Return first group matched by name"""
        return super(NsxPolicyEdgeClusterApi, self).get_by_name(
            name, ep_id, tenant=tenant)

    def create_or_overwrite(self, name, ec_id=None,
                            ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                            tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def update(self, ec_id,
               ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def delete(self, ec_id,
               ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def get_path(self, ec_id,
                 ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                 tenant=constants.POLICY_INFRA_TENANT):
        ec_def = core_defs.EdgeClusterDef(
            ep_id=ep_id, ec_id=ec_id, tenant=tenant)
        return ec_def.get_resource_full_path()

    def get_edge_node_ids(self, ec_id,
                          ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                          tenant=constants.POLICY_INFRA_TENANT):
        nodes_def = core_defs.EdgeClusterNodeDef(
            ep_id=ep_id, ec_id=ec_id, tenant=tenant)
        nodes = self._list(nodes_def)
        return [node['id'] for node in nodes]

    def get_edge_node_nsx_ids(self, ec_id,
                              ep_id=constants.DEFAULT_ENFORCEMENT_POINT,
                              tenant=constants.POLICY_INFRA_TENANT):
        nodes_def = core_defs.EdgeClusterNodeDef(
            ep_id=ep_id, ec_id=ec_id, tenant=tenant)
        nodes = self._list(nodes_def)
        return [node.get('nsx_id', node['id']) for node in nodes]


class NsxPolicyMetadataProxyApi(NsxPolicyResourceBase):
    # Currently this is used as a ready only Api
    @property
    def entry_def(self):
        return core_defs.MetadataProxyDef

    def get(self, mdproxy_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        md_def = core_defs.MetadataProxyDef(
            mdproxy_id=mdproxy_id, tenant=tenant)
        return self.policy_api.get(md_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        md_def = core_defs.MetadataProxyDef(tenant=tenant)
        return self._list(md_def)

    def get_by_name(self, name,
                    tenant=constants.POLICY_INFRA_TENANT):
        return super(NsxPolicyMetadataProxyApi, self).get_by_name(
            name, tenant=tenant)

    def create_or_overwrite(self, name, mdproxy_id=None,
                            tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def update(self, mdproxy_id,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def delete(self, mdproxy_id,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def get_path(self, mdproxy_id,
                 tenant=constants.POLICY_INFRA_TENANT):
        md_def = core_defs.MetadataProxyDef(
            mdproxy_id=mdproxy_id, tenant=tenant)
        return md_def.get_resource_full_path()


class NsxPolicyDeploymentMapApi(NsxPolicyResourceBase):
    """NSX Policy Deployment Map."""
    @property
    def entry_def(self):
        return core_defs.DeploymentMapDef

    def create_or_overwrite(self, name, map_id=None,
                            description=IGNORE,
                            ep_id=IGNORE, domain_id=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        map_id = self._init_obj_uuid(map_id)
        map_def = core_defs.DeploymentMapDef(
            map_id=map_id,
            name=name,
            description=description,
            ep_id=ep_id,
            domain_id=domain_id,
            tenant=tenant)
        self._create_or_store(map_def)
        return map_id

    def delete(self, map_id, domain_id=None,
               tenant=constants.POLICY_INFRA_TENANT):
        if not domain_id:
            # domain_id must be provided
            err_msg = (_("Cannot delete deployment maps without a domain"))
            raise exceptions.ManagerError(details=err_msg)

        map_def = core_defs.DeploymentMapDef(
            map_id=map_id, domain_id=domain_id, tenant=tenant)
        self._delete_with_retry(map_def)

    def get(self, map_id, domain_id=None,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        if not domain_id:
            # domain_id must be provided
            err_msg = (_("Cannot get deployment maps without a domain"))
            raise exceptions.ManagerError(details=err_msg)
        map_def = core_defs.DeploymentMapDef(
            map_id=map_id, domain_id=domain_id, tenant=tenant)
        return self.policy_api.get(map_def, silent=silent)

    def list(self, domain_id=None,
             tenant=constants.POLICY_INFRA_TENANT):
        if not domain_id:
            # domain_id must be provided
            err_msg = (_("Cannot list deployment maps without a domain"))
            raise exceptions.ManagerError(details=err_msg)
        map_def = core_defs.DeploymentMapDef(domain_id=domain_id,
                                             tenant=tenant)
        return self._list(map_def)

    def update(self, map_id, name=IGNORE, description=IGNORE,
               ep_id=IGNORE, domain_id=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):

        self._update(map_id=map_id,
                     name=name,
                     description=description,
                     ep_id=ep_id,
                     domain_id=domain_id,
                     tenant=tenant)


class NsxSegmentProfileBaseApi(NsxPolicyResourceBase):
    """NSX Segment Profile base API"""

    def create_or_overwrite(self, name,
                            profile_id=None,
                            description=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        profile_id = self._init_obj_uuid(profile_id)
        profile_def = self._init_def(profile_id=profile_id,
                                     name=name,
                                     description=description,
                                     tags=tags,
                                     tenant=tenant)
        self._create_or_store(profile_def)
        return profile_id

    def delete(self, profile_id, tenant=constants.POLICY_INFRA_TENANT):
        profile_def = self.entry_def(profile_id=profile_id,
                                     tenant=tenant)
        self._delete_with_retry(profile_def)

    def get(self, profile_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        profile_def = self.entry_def(profile_id=profile_id,
                                     tenant=tenant)
        return self.policy_api.get(profile_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        profile_def = self.entry_def(tenant=tenant)
        return self._list(profile_def)

    def get_by_name(self, name, tenant=constants.POLICY_INFRA_TENANT):
        return super(NsxSegmentProfileBaseApi, self).get_by_name(
            name, tenant=tenant)

    def update(self, profile_id, name=IGNORE, description=IGNORE,
               tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT):
        self._update(profile_id=profile_id,
                     name=name,
                     description=description,
                     tags=tags,
                     tenant=tenant)

    def get_path(self, profile_id, tenant=constants.POLICY_INFRA_TENANT):
        profile_def = self.entry_def(profile_id=profile_id, tenant=tenant)
        return profile_def.get_resource_full_path()


class NsxSegmentSecurityProfileApi(NsxSegmentProfileBaseApi):
    @property
    def entry_def(self):
        return core_defs.SegmentSecurityProfileDef

    def create_or_overwrite(self, name,
                            profile_id=None,
                            description=IGNORE,
                            bpdu_filter_enable=IGNORE,
                            dhcp_client_block_enabled=IGNORE,
                            dhcp_client_block_v6_enabled=IGNORE,
                            dhcp_server_block_enabled=IGNORE,
                            dhcp_server_block_v6_enabled=IGNORE,
                            non_ip_traffic_block_enabled=IGNORE,
                            ra_guard_enabled=IGNORE,
                            rate_limits_enabled=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        profile_id = self._init_obj_uuid(profile_id)
        profile_def = self._init_def(
            profile_id=profile_id,
            name=name,
            description=description,
            bpdu_filter_enable=bpdu_filter_enable,
            dhcp_client_block_enabled=dhcp_client_block_enabled,
            dhcp_client_block_v6_enabled=dhcp_client_block_v6_enabled,
            dhcp_server_block_enabled=dhcp_server_block_enabled,
            dhcp_server_block_v6_enabled=dhcp_server_block_v6_enabled,
            non_ip_traffic_block_enabled=non_ip_traffic_block_enabled,
            ra_guard_enabled=ra_guard_enabled,
            rate_limits_enabled=rate_limits_enabled,
            tags=tags,
            tenant=tenant)
        self._create_or_store(profile_def)
        return profile_id


class NsxQosProfileApi(NsxSegmentProfileBaseApi):
    @property
    def entry_def(self):
        return core_defs.QosProfileDef

    def _build_rate_limiter(self, resource_type, average_bandwidth,
                            peak_bandwidth, burst_size, enabled):
        return core_defs.QoSRateLimiter(
            resource_type=resource_type,
            average_bandwidth=average_bandwidth,
            peak_bandwidth=peak_bandwidth,
            burst_size=burst_size,
            enabled=enabled)

    def build_ingress_rate_limiter(
        self,
        average_bandwidth=None,
        peak_bandwidth=None,
        burst_size=None,
        enabled=True):
        return self._build_rate_limiter(
            resource_type=core_defs.QoSRateLimiter.INGRESS_RATE_LIMITER_TYPE,
            average_bandwidth=average_bandwidth,
            peak_bandwidth=peak_bandwidth,
            burst_size=burst_size,
            enabled=enabled)

    def build_egress_rate_limiter(
        self,
        average_bandwidth=None,
        peak_bandwidth=None,
        burst_size=None,
        enabled=True):
        return self._build_rate_limiter(
            resource_type=core_defs.QoSRateLimiter.EGRESS_RATE_LIMITER_TYPE,
            average_bandwidth=average_bandwidth,
            peak_bandwidth=peak_bandwidth,
            burst_size=burst_size,
            enabled=enabled)

    def build_dscp(self, trusted=False, priority=None):
        mode = (core_defs.QoSDscp.QOS_DSCP_TRUSTED if trusted
                else core_defs.QoSDscp.QOS_DSCP_UNTRUSTED)
        return core_defs.QoSDscp(mode=mode, priority=priority)

    def create_or_overwrite(self, name,
                            profile_id=None,
                            description=IGNORE,
                            class_of_service=IGNORE,
                            dscp=IGNORE,
                            shaper_configurations=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        profile_id = self._init_obj_uuid(profile_id)
        profile_def = self._init_def(
            profile_id=profile_id,
            name=name,
            description=description,
            class_of_service=class_of_service,
            dscp=dscp,
            shaper_configurations=shaper_configurations,
            tags=tags,
            tenant=tenant)
        self._create_or_store(profile_def)
        return profile_id


class NsxSpoofguardProfileApi(NsxSegmentProfileBaseApi):
    @property
    def entry_def(self):
        return core_defs.SpoofguardProfileDef

    def create_or_overwrite(self, name,
                            profile_id=None,
                            description=IGNORE,
                            address_binding_whitelist=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        profile_id = self._init_obj_uuid(profile_id)
        profile_def = self._init_def(
            profile_id=profile_id,
            name=name,
            description=description,
            address_binding_whitelist=address_binding_whitelist,
            tags=tags,
            tenant=tenant)
        self._create_or_store(profile_def)
        return profile_id


class NsxIpDiscoveryProfileApi(NsxSegmentProfileBaseApi):
    @property
    def entry_def(self):
        return core_defs.IpDiscoveryProfileDef


class NsxWAFProfileApi(NsxSegmentProfileBaseApi):
    @property
    def entry_def(self):
        return core_defs.WAFProfileDef


class NsxMacDiscoveryProfileApi(NsxSegmentProfileBaseApi):
    @property
    def entry_def(self):
        return core_defs.MacDiscoveryProfileDef

    def create_or_overwrite(self, name,
                            profile_id=None,
                            description=IGNORE,
                            mac_change_enabled=IGNORE,
                            mac_learning_enabled=IGNORE,
                            unknown_unicast_flooding_enabled=IGNORE,
                            mac_limit_policy=IGNORE,
                            mac_limit=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        profile_id = self._init_obj_uuid(profile_id)
        profile_def = self._init_def(
            profile_id=profile_id,
            name=name,
            description=description,
            mac_change_enabled=mac_change_enabled,
            mac_learning_enabled=mac_learning_enabled,
            unknown_unicast_flooding_enabled=unknown_unicast_flooding_enabled,
            mac_limit_policy=mac_limit_policy,
            mac_limit=mac_limit,
            tags=tags,
            tenant=tenant)
        self._create_or_store(profile_def)
        return profile_id


class NsxIpv6NdraProfileApi(NsxPolicyResourceBase):
    @property
    def entry_def(self):
        return core_defs.Ipv6NdraProfileDef

    def create_or_overwrite(self, name,
                            profile_id=None,
                            description=IGNORE,
                            ra_mode=IGNORE,
                            reachable_timer=IGNORE,
                            retransmit_interval=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        profile_id = self._init_obj_uuid(profile_id)
        profile_def = self._init_def(
            profile_id=profile_id,
            name=name,
            description=description,
            ra_mode=ra_mode,
            reachable_timer=reachable_timer,
            retransmit_interval=retransmit_interval,
            tags=tags,
            tenant=tenant)
        self._create_or_store(profile_def)
        return profile_id

    def delete(self, profile_id, tenant=constants.POLICY_INFRA_TENANT):
        profile_def = self.entry_def(profile_id=profile_id,
                                     tenant=tenant)
        self._delete_with_retry(profile_def)

    def get(self, profile_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        profile_def = self.entry_def(profile_id=profile_id,
                                     tenant=tenant)
        return self.policy_api.get(profile_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        profile_def = self.entry_def(tenant=tenant)
        return self._list(profile_def)

    def get_by_name(self, name, tenant=constants.POLICY_INFRA_TENANT):
        return super(NsxSegmentProfileBaseApi, self).get_by_name(
            name, tenant=tenant)

    def update(self, profile_id, name=IGNORE, description=IGNORE,
               ra_mode=IGNORE, reachable_timer=IGNORE,
               retransmit_interval=IGNORE,
               tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT):
        self._update(profile_id=profile_id,
                     name=name,
                     description=description,
                     ra_mode=ra_mode,
                     reachable_timer=reachable_timer,
                     retransmit_interval=retransmit_interval,
                     tags=tags,
                     tenant=tenant)


class NsxDhcpRelayConfigApi(NsxPolicyResourceBase):
    @property
    def entry_def(self):
        return core_defs.DhcpRelayConfigDef

    def create_or_overwrite(self, name,
                            config_id=None,
                            description=None,
                            server_addresses=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        config_id = self._init_obj_uuid(config_id)
        config_def = self._init_def(
            config_id=config_id,
            name=name,
            description=description,
            server_addresses=server_addresses,
            tags=tags,
            tenant=tenant)
        self._create_or_store(config_def)
        return config_id

    def delete(self, config_id, tenant=constants.POLICY_INFRA_TENANT):
        config_def = self.entry_def(config_id=config_id, tenant=tenant)
        self._delete_with_retry(config_def)

    def get(self, config_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        config_def = self.entry_def(config_id=config_id, tenant=tenant)
        return self.policy_api.get(config_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        config_def = self.entry_def(tenant=tenant)
        return self._list(config_def)

    def update(self, config_id, name=IGNORE,
               description=IGNORE,
               server_addresses=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(config_id=config_id,
                     name=name,
                     description=description,
                     server_addresses=server_addresses,
                     tags=tags,
                     tenant=tenant)


class NsxDhcpServerConfigApi(NsxPolicyResourceBase):
    @property
    def entry_def(self):
        return core_defs.DhcpServerConfigDef

    def create_or_overwrite(self, name,
                            config_id=None,
                            description=None,
                            server_addresses=IGNORE,
                            edge_cluster_path=IGNORE,
                            lease_time=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        config_id = self._init_obj_uuid(config_id)
        config_def = self._init_def(
            config_id=config_id,
            name=name,
            description=description,
            server_addresses=server_addresses,
            edge_cluster_path=edge_cluster_path,
            lease_time=lease_time,
            tags=tags,
            tenant=tenant)
        self._create_or_store(config_def)
        return config_id

    def delete(self, config_id, tenant=constants.POLICY_INFRA_TENANT):
        config_def = self.entry_def(config_id=config_id, tenant=tenant)
        self._delete_with_retry(config_def)

    def get(self, config_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        config_def = self.entry_def(config_id=config_id, tenant=tenant)
        return self.policy_api.get(config_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        config_def = self.entry_def(tenant=tenant)
        return self._list(config_def)

    def update(self, config_id, name=IGNORE,
               description=IGNORE,
               server_addresses=IGNORE,
               edge_cluster_path=IGNORE,
               lease_time=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(config_id=config_id,
                     name=name,
                     description=description,
                     server_addresses=server_addresses,
                     edge_cluster_path=edge_cluster_path,
                     lease_time=lease_time,
                     tags=tags,
                     tenant=tenant)


class NsxPolicyCertApi(NsxPolicyResourceBase):
    """NSX Policy Certificate API."""
    @property
    def entry_def(self):
        return core_defs.CertificateDef

    def create_or_overwrite(self, name, certificate_id=None,
                            pem_encoded=IGNORE, private_key=IGNORE,
                            passphrase=IGNORE,
                            key_algo=IGNORE,
                            description=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        certificate_id = self._init_obj_uuid(certificate_id)
        certificate_def = self._init_def(certificate_id=certificate_id,
                                         name=name,
                                         private_key=private_key,
                                         pem_encoded=pem_encoded,
                                         passphrase=passphrase,
                                         key_algo=key_algo,
                                         description=description,
                                         tags=tags,
                                         tenant=tenant)

        self._create_or_store(certificate_def)
        return certificate_id

    def delete(self, certificate_id,
               tenant=constants.POLICY_INFRA_TENANT):
        certificate_def = self.entry_def(certificate_id=certificate_id,
                                         tenant=tenant)
        self._delete_with_retry(certificate_def)

    def get(self, certificate_id, tenant=constants.POLICY_INFRA_TENANT,
            silent=False):
        certificate_def = self.entry_def(certificate_id=certificate_id,
                                         tenant=tenant)
        return self.policy_api.get(certificate_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        certificate_def = self.entry_def(tenant=tenant)
        return self._list(certificate_def)

    def find_cert_with_pem(self, cert_pem,
                           tenant=constants.POLICY_INFRA_TENANT):
        """Find NSX certificates with specific pem and return their IDs"""
        # First fix Dos to unix possible issues, as the NSX backed also does
        nsx_style_pem = cert_pem.replace('\r\n', '\n')
        certs = self.list(tenant=tenant)
        cert_ids = [cert['id'] for cert in certs
                    if cert['pem_encoded'] == nsx_style_pem]
        return cert_ids

    def update(self, certificate_id, name=IGNORE,
               pem_encoded=IGNORE, private_key=IGNORE,
               passphrase=IGNORE, key_algo=IGNORE, description=IGNORE,
               tags=IGNORE, tenant=constants.POLICY_INFRA_TENANT):
        self._update(certificate_id=certificate_id,
                     name=name,
                     description=description,
                     tags=tags,
                     private_key=private_key,
                     pem_encoded=pem_encoded,
                     passphrase=passphrase,
                     key_algo=key_algo,
                     tenant=tenant)

    def get_path(self, certificate_id, tenant=constants.POLICY_INFRA_TENANT):
        c_def = self.entry_def(certificate_id=certificate_id, tenant=tenant)
        return c_def.get_resource_full_path()

    def wait_until_realized(self, certificate_id, entity_type=None,
                            tenant=constants.POLICY_INFRA_TENANT,
                            sleep=None, max_attempts=None):
        cert_def = self.entry_def(
            certificate_id=certificate_id, tenant=tenant)
        return self._wait_until_realized(
            cert_def, entity_type=entity_type,
            sleep=sleep, max_attempts=max_attempts)


class NsxPolicyExcludeListApi(NsxPolicyResourceBase):
    """NSX Policy Exclude list."""

    @property
    def entry_def(self):
        return core_defs.ExcludeListDef

    def create_or_overwrite(self, members=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        exclude_list_def = self._init_def(members=members,
                                          tenant=tenant)

        self._create_or_store(exclude_list_def)

    def delete(self, tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def get(self, tenant=constants.POLICY_INFRA_TENANT, silent=False):
        exclude_list_def = self.entry_def(tenant=tenant)
        return self.policy_api.get(exclude_list_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def update(self, members=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    # TODO(asarfaty): Add support for add/remove member


class NsxPolicyTier0RouteMapApi(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.Tier0RouteMapDef

    def create_or_overwrite(self, name, tier0_id,
                            route_map_id=None,
                            entries=IGNORE,
                            description=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):
        route_map_id = self._init_obj_uuid(route_map_id)
        route_map_def = self._init_def(tier0_id=tier0_id,
                                       route_map_id=route_map_id,
                                       name=name,
                                       entries=entries,
                                       description=description,
                                       tags=tags,
                                       tenant=tenant)
        self._create_or_store(route_map_def)
        return route_map_id

    def delete(self, tier0_id, route_map_id,
               tenant=constants.POLICY_INFRA_TENANT):
        route_map_def = self.entry_def(tier0_id=tier0_id,
                                       route_map_id=route_map_id,
                                       tenant=tenant)
        self._delete_with_retry(route_map_def)

    def get(self, tier0_id, route_map_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        route_map_def = self.entry_def(tier0_id=tier0_id,
                                       route_map_id=route_map_id,
                                       tenant=tenant)
        return self.policy_api.get(route_map_def, silent=silent)

    def list(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        route_map_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self._list(route_map_def)

    def update(self, name, tier0_id,
               route_map_id,
               entries,
               description=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT,
               force=False):
        self._update(tier0_id=tier0_id,
                     route_map_id=route_map_id,
                     name=name,
                     entries=entries,
                     description=description,
                     tags=tags,
                     tenant=tenant,
                     force=force)

    def build_route_map_entry(self, action, community_list_matches=None,
                              prefix_list_matches=None, entry_set=None):
        return core_defs.RouteMapEntry(action, community_list_matches,
                                       prefix_list_matches, entry_set)

    def build_route_map_entry_set(self, local_preference=100,
                                  as_path_prepend=None, community=None,
                                  med=None, weight=None):
        return core_defs.RouteMapEntrySet(local_preference, as_path_prepend,
                                          community, med, weight)

    def build_community_match_criteria(self, criteria, match_operator=None):
        return core_defs.CommunityMatchCriteria(criteria, match_operator)


class NsxPolicyTier0PrefixListApi(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.Tier0PrefixListDef

    def create_or_overwrite(self, name, tier0_id,
                            prefix_list_id=None,
                            prefixes=IGNORE,
                            description=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_INFRA_TENANT):

        prefix_list_id = self._init_obj_uuid(prefix_list_id)
        prefix_list_def = self._init_def(tier0_id=tier0_id,
                                         prefix_list_id=prefix_list_id,
                                         name=name,
                                         prefixes=prefixes,
                                         description=description,
                                         tags=tags,
                                         tenant=tenant)
        self._create_or_store(prefix_list_def)
        return prefix_list_id

    def delete(self, tier0_id, prefix_list_id,
               tenant=constants.POLICY_INFRA_TENANT):
        prefix_list_def = self.entry_def(tier0_id=tier0_id,
                                         prefix_list_id=prefix_list_id,
                                         tenant=tenant)
        self._delete_with_retry(prefix_list_def)

    def get(self, tier0_id, prefix_list_id,
            tenant=constants.POLICY_INFRA_TENANT, silent=False):
        prefix_list_def = self.entry_def(tier0_id=tier0_id,
                                         prefix_list_id=prefix_list_id,
                                         tenant=tenant)
        return self.policy_api.get(prefix_list_def, silent=silent)

    def list(self, tier0_id, tenant=constants.POLICY_INFRA_TENANT):
        prefix_list_def = self.entry_def(tier0_id=tier0_id, tenant=tenant)
        return self._list(prefix_list_def)

    def update(self, name, tier0_id,
               prefix_list_id,
               prefixes,
               description=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        self._update(tier0_id=tier0_id,
                     prefix_list_id=prefix_list_id,
                     name=name,
                     prefixes=prefixes,
                     description=description,
                     tags=tags,
                     tenant=tenant)

    def build_prefix_entry(self, network, le=None, ge=None,
                           action=constants.ADV_RULE_PERMIT):
        return core_defs.PrefixEntry(network, le, ge, action)


class NsxPolicyGlobalConfig(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.GlobalConfigDef

    def create_or_overwrite(self, tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def delete(self, tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def get(self, tenant=constants.POLICY_INFRA_TENANT, silent=False):
        global_config_def = self.entry_def(tenant=tenant)
        return self.policy_api.get(global_config_def, silent=silent)

    def list(self, tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def update(self, members=IGNORE,
               tenant=constants.POLICY_INFRA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    def _set_l3_forwarding_mode(self, mode, tenant):
        # Using PUT as PATCH is not supported for this API.
        config = self.get()
        if config['l3_forwarding_mode'] != mode:
            config['l3_forwarding_mode'] = mode
            config_def = self.entry_def(tenant=tenant)
            path = config_def.get_resource_path()
            self.policy_api.client.update(path, config)

    def enable_ipv6(self, tenant=constants.POLICY_INFRA_TENANT):
        return self._set_l3_forwarding_mode('IPV4_AND_IPV6', tenant)

    def disable_ipv6(self, tenant=constants.POLICY_INFRA_TENANT):
        return self._set_l3_forwarding_mode('IPV4_ONLY', tenant)


class NsxPolicyObjectRolePermissionGroupApi(NsxPolicyResourceBase):

    @property
    def entry_def(self):
        return core_defs.ObjectRolePermissionGroupDef

    # This will send a PATCH call: /policy/api/v1/aaa/object-permissions.
    def create_or_overwrite(self, name, operation, path_prefix, role_name,
                            orbac_id=IGNORE,
                            description=IGNORE,
                            inheritance_disabled=IGNORE,
                            rule_disabled=IGNORE,
                            tags=IGNORE,
                            tenant=constants.POLICY_AAA_TENANT):

        orbac_def = self._init_def(name=name,
                                   operation=operation,
                                   path_prefix=path_prefix,
                                   role_name=role_name,
                                   orbac_id=orbac_id,
                                   description=description,
                                   inheritance_disabled=inheritance_disabled,
                                   rule_disabled=rule_disabled,
                                   tags=tags,
                                   tenant=tenant,
                                   patch=True)
        self.policy_api.create_or_update(orbac_def)

    # This will send a PATCH call: /policy/api/v1/aaa/object-permissions.
    def update(self, name, operation, path_prefix, role_name,
               orbac_id=IGNORE,
               description=IGNORE,
               inheritance_disabled=IGNORE,
               rule_disabled=IGNORE,
               tags=IGNORE,
               tenant=constants.POLICY_AAA_TENANT):
        self._update(name=name,
                     operation=operation,
                     path_prefix=path_prefix,
                     role_name=role_name,
                     orbac_id=orbac_id,
                     description=description,
                     inheritance_disabled=inheritance_disabled,
                     rule_disabled=rule_disabled,
                     tags=tags,
                     tenant=tenant,
                     patch=True)

    def get(self, path_prefix, role_name, tenant=constants.POLICY_AAA_TENANT):
        err_msg = (_("This action is not supported"))
        raise exceptions.ManagerError(details=err_msg)

    # This will send a GET call:
    # /policy/api/v1/aaa/object-permissions?path_prefix=...&role_name=...
    def list(self, path_prefix=None, role_name=None,
             tenant=constants.POLICY_AAA_TENANT):
        orbac_def = self.entry_def(path_prefix=path_prefix,
                                   role_name=role_name,
                                   tenant=tenant)
        return self._list(orbac_def)

    # This will send a DELETE call:
    # /policy/api/v1/aaa/object-permissions?path_prefix=...&role_name=...
    # path_prefix and role_name must be specified in the url as they are
    # the identifier for an ORBAC object on NSX. Otherwise, NSX will
    # still return success but actually delete nothing.
    def delete(self, path_prefix, role_name,
               tenant=constants.POLICY_AAA_TENANT):
        orbac_def = self.entry_def(path_prefix=path_prefix,
                                   role_name=role_name,
                                   tenant=tenant)
        self._delete_with_retry(orbac_def)
