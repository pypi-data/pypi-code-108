import ducts_client.event_listeners

class DuctEventListener(ducts_client.event_listeners.DuctEventListener):
    def __init__(self):
        super().__init__()
        self.handlers = {}

    def add_handler(self, event_name, handler):
        self.handlers[event_name].append(handler)

    def get_handlers(self, event_name):
        if event_name in self.handlers:
            return self.handlers[event_name]
        else:
            raise Exception(f"Event named '{event_name}' is not found")
        
    def on(self, names, handler):
        if isinstance(names, str):  names = [names]
        for name in names:  self.add_handler(name, handler)

class ResourceEventListener(DuctEventListener):
    def __init__(self):
        super().__init__()

        self.handlers = {
            "list_projects": [],
            "create_project": [],
            "get_event_history": [],
            "set_event_history": [],
            "list_projects": [],
            "create_project": [],
            "get_project_scheme": [],
            "create_templates": [],
            "list_template_presets": [],
            "list_templates": [],
            "get_responses_for_template": [],
            "get_responses_for_nanotask": [],
            "get_nanotasks": [],
            "upload_nanotasks": [],
            "delete_nanotasks": [],
            "update_nanotask_num_assignable": [],
            "create_session": [],
            "get_template_node": [],
            "set_response": [],
            "check_platform_worker_id_existence_for_project": [],
        }

class MTurkEventListener(DuctEventListener):
    def __init__(self):
        super().__init__()

        self.handlers = {
            "get_credentials": [],
            "set_credentials": [],
            "clear_credentials": [],
            "set_sandbox": [],
            "get_hit_types": [],
            "create_hit_type": [],
            "create_hits_with_hit_type": [],
            "list_qualifications": [],
            "list_hits": [],
            "list_hits_for_hit_type": [],
            "expire_hits": [],
            "delete_hits": [],
            "create_qualification": [],
            "associate_qualifications_with_workers": [],
            "list_workers": [],
            "list_workers_with_qualification_type": [],
            "delete_qualifications": [],
            "list_assignments": [],
            "list_assignments_for_hits": [],
            "approve_assignments": [],
            "reject_assignments": [],
            "get_assignments": [],
        }
