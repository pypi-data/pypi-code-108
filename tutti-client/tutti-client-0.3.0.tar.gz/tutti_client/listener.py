import inspect

import ducts_client

class DuctEventListener(ducts_client.event_listeners.DuctEventListener):
    def __init__(self, duct):
        self._duct = duct
        self._handlers = {}

    def on(self, names, success = None, error = None, complete = None):
        print(inspect.getargspec(success).args)
        if not (inspect.iscoroutinefunction(success) or success is None) \
            or not (inspect.iscoroutinefunction(error) or error is None) \
            or not (inspect.iscoroutinefunction(complete) or complete is None):
            raise Exception('handler must be a coroutine function')

        if type(names) == str:
            names = [names]
        for name in names:
            if name not in self._handlers:
                raise Exception(f'[{name}] is not defined')
            if success: self._handlers[name]['success'].append(success)
            if error: self._handlers[name]['error'].append(error)
            if complete: self._handlers[name]['complete'].append(complete)

    async def _handle(self, source, name, rid, data):
        if data is None: return

        try:
            handlers = self._handlers[name]
            if data['success']: [await handler(data['content']) for handler in handlers['success']]
            else: [await handler(data['content']) for handler in handlers['error']]
            [await handler(data['content']) for handler in handlers['complete']]
        except Exception as e:
            raise Exception(e)

    def _set_default_tutti_handlers(self, methods):
        for method in methods:
            self._handlers[method] = { 'success': [], 'error': [], 'complete': [] }

    def register_handlers(self, source, listener_event_relay_map):
        for name, eid in listener_event_relay_map.items():
            def coro_gen(name):
                async def _coro(rid, eid, data):
                    await self._handle(source, name, rid, data)
                return _coro

            self._duct.set_event_handler(eid, coro_gen(name))

        self._set_default_tutti_handlers(listener_event_relay_map.keys())

class ResourceEventListener(DuctEventListener):
    def __init__(self, duct):
        super().__init__(duct)

        listener_event_relay_map = {
                'get_web_service_descriptor':
                    duct.EVENT['SYSTEM_GET_WSD'],
                'sign_up':
                    duct.EVENT['AUTHENTICATION_SIGN_UP'],
                'sign_in':
                    duct.EVENT['AUTHENTICATION_SIGN_IN'],
                'sign_out':
                    duct.EVENT['AUTHENTICATION_SIGN_OUT'],
                'get_user_ids':
                    duct.EVENT['ACCOUNT_LIST_IDS'],
                'delete_account':
                    duct.EVENT['ACCOUNT_DELETE'],
                'check_project_diff':
                    duct.EVENT['SYSTEM_BUILD_CHECK_PROJECT_DIFF'],
                'rebuild_project':
                    duct.EVENT['SYSTEM_BUILD_REBUILD_PROJECT'],
                'list_projects':
                    duct.EVENT['PROJECT_LIST'],
                'create_project':
                    duct.EVENT['PROJECT_ADD'],
                'delete_project':
                    duct.EVENT['PROJECT_DELETE'],
                'get_project_scheme':
                    duct.EVENT['PROJECT_GET_SCHEME'],
                'create_template':
                    duct.EVENT['PROJECT_ADD_TEMPLATE'],
                'delete_template':
                    duct.EVENT['PROJECT_DELETE_TEMPLATE'],
                'list_templates':
                    duct.EVENT['PROJECT_LIST_TEMPLATES'],
                'list_template_presets':
                    duct.EVENT['PROJECT_LIST_TEMPLATE_PRESETS'],
                'list_responses_for_project':
                    duct.EVENT['RESPONSE_LIST_FOR_PROJECT'],
                'list_responses_for_template':
                    duct.EVENT['RESPONSE_LIST_FOR_TEMPLATE'],
                'list_responses_for_nanotask':
                    duct.EVENT['RESPONSE_LIST_FOR_NANOTASK'],
                'list_responses_for_worker':
                    duct.EVENT['RESPONSE_LIST_FOR_WORKER'],
                'list_responses_for_work_session':
                    duct.EVENT['RESPONSE_LIST_FOR_WORK_SESSION'],
                'list_projects_with_responses':
                    duct.EVENT['RESPONSE_LIST_PROJECTS'],
                'list_templates_with_responses':
                    duct.EVENT['RESPONSE_LIST_TEMPLATES'],
                'list_nanotasks_with_responses':
                    duct.EVENT['RESPONSE_LIST_NANOTASKS'],
                'list_workers_with_responses':
                    duct.EVENT['RESPONSE_LIST_WORKERS'],
                'list_work_sessions_with_responses':
                    duct.EVENT['RESPONSE_LIST_WORK_SESSIONS'],
                'list_workers_for_project':
                    duct.EVENT['WORKER_GET_FOR_PLATFORM_WORKER_ID'],
                'list_nanotasks':
                    duct.EVENT['NANOTASK_LIST'],
                'create_nanotasks':
                    duct.EVENT['NANOTASK_ADD_MULTI_FOR_TEMPLATE'],
                'delete_nanotasks':
                    duct.EVENT['NANOTASK_DELETE'],
                'create_nanotask_group':
                    duct.EVENT['NANOTASK_GROUP_ADD'],
                'list_nanotask_groups':
                    duct.EVENT['NANOTASK_GROUP_LIST'],
                'get_nanotask_group':
                    duct.EVENT['NANOTASK_GROUP_GET'],
                'delete_nanotask_group':
                    duct.EVENT['NANOTASK_GROUP_DELETE'],
                'list_node_sessions_for_work_session':
                    duct.EVENT['NODE_SESSION_LIST_FOR_WORK_SESSION'],
            }

        self.register_handlers('resource', listener_event_relay_map)


class MTurkEventListener(DuctEventListener):
    def __init__(self, duct):
        super().__init__(duct)

        listener_event_relay_map = {
                'get_active_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_GET_ACTIVE_CREDENTIALS'],
                'set_active_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_SET_ACTIVE_CREDENTIALS'],
                'list_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_LIST_CREDENTIALS'],
                'get_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_GET_CREDENTIALS'],
                'delete_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_DELETE_CREDENTIALS'],
                'rename_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_RENAME_CREDENTIALS'],
                'add_credentials':
                    duct.EVENT['MARKETPLACE_MTURK_ADD_CREDENTIALS'],
                'set_active_sandbox_mode':
                    duct.EVENT['MARKETPLACE_MTURK_SET_ACTIVE_SANDBOX_MODE'],
                'exec_boto3':
                    duct.EVENT['MARKETPLACE_MTURK_EXEC_BOTO3'],
                'list_hittypes':
                    duct.EVENT['MARKETPLACE_MTURK_HIT_TYPE_LIST'],
                'list_tutti_hit_batches':
                    duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_LIST'],
                'list_tutti_hit_batches_with_hits':
                    duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_LIST_WITH_HITS'],
                'create_tutti_hit_batch':
                    duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_CREATE'],
                'add_hits_to_tutti_hit_batch':
                    duct.EVENT['MARKETPLACE_MTURK_HIT_ADD_FOR_TUTTI_HIT_BATCH'],
                'delete_tutti_hit_batch':
                    duct.EVENT['MARKETPLACE_MTURK_TUTTI_HIT_BATCH_DELETE'],
                'list_qualification_types':
                    duct.EVENT['MARKETPLACE_MTURK_QUALIFICATION_TYPE_LIST'],
                'create_qualification_type':
                    duct.EVENT['MARKETPLACE_MTURK_QUALIFICATION_TYPE_CREATE'],
                'delete_qualification_types':
                    duct.EVENT['MARKETPLACE_MTURK_QUALIFICATION_TYPE_DELETE'],
                'associate_qualifications_with_workers':
                    duct.EVENT['MARKETPLACE_MTURK_WORKER_ASSOCIATE_QUALIFICATIONS'],
                'list_hits_for_tutti_hit_batch':
                    duct.EVENT['MARKETPLACE_MTURK_HIT_LIST_FOR_TUTTI_HIT_BATCH'],
                'expire_hits':
                    duct.EVENT['MARKETPLACE_MTURK_HIT_EXPIRE'],
                'delete_hits':
                    duct.EVENT['MARKETPLACE_MTURK_HIT_DELETE'],
                'list_workers':
                    duct.EVENT['MARKETPLACE_MTURK_WORKER_LIST'],
                'notify_workers':
                    duct.EVENT['MARKETPLACE_MTURK_WORKER_NOTIFY'],
                'list_assignments_for_tutti_hit_batch':
                    duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_LIST_FOR_TUTTI_HIT_BATCH'],
                'approve_assignments':
                    duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_APPROVE'],
                'reject_assignments':
                    duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_REJECT'],
                'send_bonus':
                    duct.EVENT['MARKETPLACE_MTURK_ASSIGNMENT_SEND_BONUS'],
            }

        self.register_handlers('mturk', listener_event_relay_map)
