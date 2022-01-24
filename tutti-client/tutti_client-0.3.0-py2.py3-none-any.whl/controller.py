import inspect
import hashlib
from collections import namedtuple
from typing import Optional

from .errors import TuttiServerError

class Controller:
    def __init__(self, duct):
        self._duct = duct
        self._access_token = None
        self._register_send_call()

    async def _send(self, eid, data):
        rid = self._duct.next_rid()
        return await self._duct.send(rid, eid, data)

    async def _called(self, eid, data):
        ret = await self._duct.call(eid, data)
        if ret['success']:
            return ret['content']
        else:
            raise TuttiServerError(ret)

    def _call_or_send(self, eid, data, called = True):
        data['access_token'] = self._access_token
        f = self._called if called else self._send
        return f(eid, data)

    def _curried(self, method_name, called):
        def f(**kwargs):
            return getattr(self, method_name)(**kwargs, called=called)
        return f

    def _register_send_call(self):
        methods = [name for (name,f) in inspect.getmembers(self, predicate=inspect.ismethod) if not name.startswith('_')]
        for name in methods:
            getattr(self.__class__, name).send = self._curried(name, called=False)
            getattr(self.__class__, name).call = self._curried(name, called=True)

class ResourceController(Controller):
    def __init__(self, duct):
        super().__init__(duct)

    async def get_web_service_descriptor(self, called = True):
        return await self._call_or_send(self._duct.EVENT['SYSTEM_GET_WSD'], {}, called = called)

    async def sign_up(self, user_name: str, password_hash: Optional[str] = None, privilege_ids: list = [], called = True, **kwargs):
        if 'password' in kwargs:
            password_hash = hashlib.md5(kwargs['password'].encode()).hexdigest()
        return await self._call_or_send(
                self._duct.EVENT['AUTHENTICATION_SIGN_UP'],
                {
                    'user_name': user_name,
                    'password_hash': password_hash,
                    'privilege_ids': privilege_ids
                },
                called = called
            )

    async def sign_in(self, user_name: str = None, password_hash: str = None, access_token: str = None, called = True, **kwargs):
        if 'password' in kwargs:
            password_hash = hashlib.md5(kwargs['password'].encode()).hexdigest()
        return await self._call_or_send(
                self._duct.EVENT['AUTHENTICATION_SIGN_IN'],
                {
                    'user_name': user_name,
                    'password_hash': password_hash,
                    'access_token': access_token
                },
                called = called
            )

    async def sign_out(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['AUTHENTICATION_SIGN_OUT'],
                {},
                called = called
            )

    async def get_user_ids(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['ACCOUNT_LIST_IDS'],
                {},
                called = called
            )

    async def delete_account(self, user_id: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['ACCOUNT_DELETE'],
                { 'user_id': user_id },
                called = called
            )

    async def check_project_diff(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['SYSTEM_BUILD_CHECK_PROJECT_DIFF'],
                { 'project_name': project_name },
                called = called
            )

    async def rebuild_project(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['SYSTEM_BUILD_REBUILD_PROJECT'],
                { 'project_name': project_name },
                called = called
            )

    async def list_projects(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_LIST'],
                {},
                called = called
            )

    async def create_project(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_ADD'],
                { 'project_name': project_name },
                called = called
            )

    async def delete_project(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_DELETE'],
                { 'project_name': project_name },
                called = called
            )

    async def get_project_scheme(self, project_name: str, cached, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_GET_SCHEME'],
                { 'project_name': project_name, cached: cached },
                called = called
            )

    async def create_template(self, project_name: str, template_name: str, preset_group_name: str, preset_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_ADD_TEMPLATE'],
                {
                    'project_name': project_name,
                    'template_name': template_name,
                    'preset_group_name': preset_group_name,
                    'preset_name': preset_name
                },
                called = called
            )

    async def delete_template(self, project_name: str, template_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_DELETE_TEMPLATE'],
                { 'project_name': project_name, 'template_name': template_name },
                called = called
            )

    async def list_templates(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_LIST_TEMPLATES'],
                { 'project_name': project_name },
                called = called
            )

    async def list_template_presets(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['PROJECT_LIST_TEMPLATE_PRESETS'],
                { 'project_name': project_name },
                called = called
            )

    async def list_responses_for_project(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_FOR_PROJECT'],
                { 'project_name': project_name },
                called = called
            )

    async def list_responses_for_template(self, project_name: str, template_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_FOR_TEMPLATE'],
                { 'project_name': project_name, 'template_name': template_name },
                called = called
            )

    async def list_responses_for_nanotask(self, nanotask_id: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_FOR_NANOTASK'],
                { 'nanotask_id': nanotask_id },
                called = called
            )

    async def list_responses_for_worker(self, worker_id: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_FOR_WORKER'],
                { worker_id: worker_id },
                called = called
            )

    async def list_responses_for_work_session(self, work_session_id: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_FOR_WORK_SESSION'],
                { work_session_id: work_session_id },
                called = called
            )

    async def list_projects_with_responses(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_PROJECTS'],
                {},
                called = called
            )

    async def list_templates_with_responses(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_TEMPLATES'],
                { project_name: project_name },
                called = called
            )

    async def list_nanotasks_with_responses(self, project_name: str, template_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_NANOTASKS'],
                { project_name: project_name, template_name: template_name },
                called = called
            )

    async def list_workers_with_responses(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_WORKERS'],
                { project_name: project_name },
                called = called
            )

    async def list_work_sessions_with_responses(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['RESPONSE_LIST_WORK_SESSIONS'],
                { project_name: project_name },
                called = called
            )

    async def list_workers_for_project(self, project_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['WORKER_LIST_FOR_PROJECT'],
                { project_name: project_name },
                called = called
            )

    async def list_nanotasks(self, project_name: str, template_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_LIST'],
                { project_name: project_name, template_name: template_name },
                called = called
            )

    async def create_nanotasks(self, project_name: str, template_name: str, nanotasks: list, tag: str, priority: int, num_assignable: int, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_ADD_MULTI_FOR_TEMPLATE'],
                {
                    project_name: project_name,
                    template_name: template_name,
                    nanotasks: nanotasks,
                    tag: tag,
                    priority: priority,
                    num_assignable: num_assignable
                },
                called = called
            )

    async def delete_nanotasks(self, nanotask_ids: list, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_DELETE'],
                { nanotask_ids: nanotask_ids },
                called = called
            )

    async def create_nanotask_group(self, name: str, nanotask_ids: list, project_name: str, template_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_GROUP_ADD'],
                { name: name, nanotask_ids: nanotask_ids, project_name: project_name, template_name: template_name },
                called = called
            )

    async def list_nanotask_groups(self, project_name: str, template_name: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_GROUP_LIST'],
                { project_name: project_name, template_name: template_name },
                called = called
            )

    async def get_nanotask_group(self, nanotask_group_id: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_GROUP_GET'],
                { nanotask_group_id: nanotask_group_id },
                called = called
            )

    async def delete_nanotask_group(self, nanotask_group_id: str, called = True):
        return await self._call_or_send(
                self._duct.EVENT['NANOTASK_GROUP_DELETE'],
                { nanotask_group_id: nanotask_group_id },
                called = called
            )

class MTurkController(Controller):
    def __init__(self, duct):
        super().__init__(duct)

    async def get_active_credentials(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_GET_ACTIVE_CREDENTIALS'],
                {},
                called = called
            )
    async def set_active_credentials(self, credentials_id, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_SET_ACTIVE_CREDENTIALS'],
                { credentials_id: credentials_id },
                called = called
            )
    async def list_credentials(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_LIST_CREDENTIALS'],
                {},
                called = called
            )
    async def get_credentials(self, credentials_id, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_GET_CREDENTIALS'],
                { credentials_id: credentials_id },
                called = called
            )
    async def delete_credentials(self, credentials_id, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_DELETE_CREDENTIALS'],
                { credentials_id: credentials_id },
                called = called
            )
    async def rename_credentials(self, credentials_id, label, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_RENAME_CREDENTIALS'],
                { credentials_id: credentials_id, label: label },
                called = called
            )
    async def add_credentials(self, access_key_id, secret_access_key, label, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_ADD_CREDENTIALS'],
                { access_key_id: access_key_id, secret_access_key: secret_access_key, label: label },
                called = called
            )
    async def set_active_sandbox_mode(self, is_sandbox, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_SET_ACTIVE_SANDBOX_MODE'],
                { is_sandbox: is_sandbox },
                called = called
            )
    async def exec_boto3(self, method, parameters, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_EXEC_BOTO3'],
                { method: method, parameters: parameters },
                called = called
            )
    async def expire_hits(self, request_id, hit_ids, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_HIT_EXPIRE'],
                { request_id: request_id, hit_ids: hit_ids },
                called = called
            )
    async def delete_hits(self, request_id, hit_ids, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_HIT_DELETE'],
                { request_id: request_id, hit_ids: hit_ids },
                called = called
            )
    async def list_hits_for_tutti_hit_batch(self, batch_id, cached, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_HIT_LIST_FOR_TUTTI_HIT_BATCH'],
                { batch_id: batch_id, cached: cached },
                called = called
            )
    async def list_tutti_hit_batches(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_LIST'],
                {},
                called = called
            )
    async def list_tutti_hit_batches_with_hits(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_LIST_WITH_HITS'],
                {},
                called = called
            )
    async def create_tutti_hit_batch(self, name, project_name, hit_type_params, hit_params, num_hits, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_CREATE'],
                {
                    name: name,
                    project_name: project_name,
                    hit_type_params: hit_type_params,
                    hit_params: hit_params,
                    num_hits : num_hits
                },
                called = called
            )
    async def add_hits_to_tutti_hit_batch(self, batch_id, hit_params, num_hits, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_HIT_ADD_FOR_TUTTI_HIT_BATCH'],
                { batch_id: batch_id, hit_params: hit_params, num_hits : num_hits },
                called = called
            )
    async def delete_tutti_hit_batch(self, request_id, batch_id, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_DELETE'],
                { request_id: request_id, batch_id: batch_id },
                    called = called
            )
    async def list_hit_types(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_HIT_TYPE_LIST'],
                {},
                called = called
            )
    async def list_qualification_types(self, query, only_user_defined, cached, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_QUALIFICATION_TYPE_LIST'],
                { query: query, only_user_defined: only_user_defined, cached : cached },
                called = called
            )
    async def create_qualification_type(self, name, description, auto_granted, qualification_type_status, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_QUALIFICATION_TYPE_CREATE'],
                {
                    name: name,
                    description: description,
                    auto_granted: auto_granted,
                    qualification_type_status : qualification_type_status
                },
                called = called
            )
    async def delete_qualification_types(self, qualification_type_ids, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_QUALIFICATION_TYPE_DELETE'],
                { qualification_type_ids : qualification_type_ids },
                called = called
            )
    async def list_workers(self, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_WORKER_LIST'],
                {},
                called = called
            )
    async def notify_workers(self, subject, message_text, worker_ids, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_WORKER_NOTIFY'],
                { subject: subject, message_text: message_text, worker_ids : worker_ids },
                called = called
            )
    async def associate_qualifications_with_workers(self, qualification_type_id, worker_ids, integer_value, send_notification, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_WORKER_ASSOCIATE_QUALIFICATIONS'],
                {
                    qualification_type_id: qualification_type_id,
                    worker_ids: worker_ids,
                    integer_value: integer_value,
                    send_notification : send_notification
                },
                called = called
            )
    async def list_assignments_for_tutti_hit_batch(self, batch_id, cached, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_LIST_FOR_TUTTI_HIT_BATCH'],
                { batch_id: batch_id, cached : cached },
                called = called
            )
    async def approve_assignments(self, assignment_ids, requester_feedback, override_rejection, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_APPROVE'],
                {
                    assignment_ids: assignment_ids,
                    requester_feedback: requester_feedback,
                    override_rejection : override_rejection
                },
                called = called
            )
    async def reject_assignments(self, assignment_ids, requester_feedback, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_REJECT'],
                { assignment_ids: assignment_ids, requester_feedback : requester_feedback },
                called = called
            )
    async def send_bonus(self, worker_ids, bonus_amount, assignment_ids, reason, called = True):
        return await self._call_or_send(
                self._duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_SEND_BONUS'],
                {
                    worker_ids: worker_ids,
                    bonus_amount: bonus_amount,
                    assignment_ids: assignment_ids,
                    reason : reason
                },
                called = called
            )
