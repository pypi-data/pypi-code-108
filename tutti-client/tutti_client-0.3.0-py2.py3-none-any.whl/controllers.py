class ResourceController:
    def __init__(self, duct):
        self.duct = duct

    async def get_event_history(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["EVENT_HISTORY"], None)

    async def set_event_history(self, eid, query):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["EVENT_HISTORY"], [eid, query])

    async def list_projects(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["LIST_PROJECTS"], None)

    async def create_project(self, ProjectName):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["CREATE_PROJECT"], { "ProjectName": ProjectName })

    async def get_project_scheme(self, ProjectName, Cached):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["GET_PROJECT_SCHEME"],
                                        { "ProjectName": ProjectName, "Cached": Cached })

    async def create_templates(self, ProjectName, TemplateNames, PresetEnvName, PresetTemplateName):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["CREATE_TEMPLATES"],
                                        { "ProjectName": ProjectName, "TemplateNames": TemplateNames,
                                          "PresetEnvName": PresetEnvName, "PresetTemplateName": PresetTemplateName })

    async def list_template_presets(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["LIST_TEMPLATE_PRESETS"], None)

    async def list_templates(self, ProjectName):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["LIST_TEMPLATES"], { "ProjectName": ProjectName })

    async def get_responses_for_template(self, ProjectName, TemplateName):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["GET_RESPONSES_FOR_TEMPLATE"],
                                        { "ProjectName": ProjectName, "TemplateName": TemplateName })

    async def get_responses_for_nanotask(self, NanotaskId):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["GET_RESPONSES_FOR_NANOTASK"], { "NanotaskId": NanotaskId })

    async def get_nanotasks(self, ProjectName, TemplateName):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["GET_NANOTASKS"],
                                        { "ProjectName": ProjectName, "TemplateName": TemplateName })

    async def upload_nanotasks(self, ProjectName, TemplateName, Nanotasks, NumAssignable, Priority, TagName):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["UPLOAD_NANOTASKS"],
                                        { "ProjectName": ProjectName, "TemplateName": TemplateName,
                                          "Nanotasks": Nanotasks, "NumAssignable": NumAssignable,
                                          "Priority": Priority, "TagName": TagName })

    async def delete_nanotasks(self, ProjectName, TemplateName, NanotaskIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["DELETE_NANOTASKS"],
                                        { "ProjectName": ProjectName, "TemplateName": TemplateName, "NanotaskIds": NanotaskIds })

    async def update_nanotask_num_assignable(self, ProjectName, TemplateName, NanotaskId, NumAssignable):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["UPDATE_NANOTASK_NUM_ASSIGNABLE"],
                                        { "ProjectName": ProjectName, "TemplateName": TemplateName,
                                          "NanotaskId": NanotaskId, "NumAssignable": NumAssignable })

    async def create_session(self, ProjectName, PlatformWorkerId, ClientToken, Platform):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["SESSION"], { "Command": "Create",
                                        "ProjectName": ProjectName, "TemplateName": TemplateName,
                                        "NanotaskId": NanotaskId, "NumAssignable": NumAssignable })

    async def get_template_node(self, Target, WorkSessionId, NodeSessionId):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["SESSION"], { "Command": "Get",
                                        "Target": Target, "WorkSessionId": WorkSessionId, "NodeSessionId": NodeSessionId })

    async def set_response(self, WorkSessionId, NodeSessionId, Answers):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["SESSION"], { "Command": "SetResponse",
                                        "WorkSessionId": WorkSessionId, "NodeSessionId": NodeSessionId, "Answers": Answers })

    async def check_platform_worker_id_existence_for_project(self, ProjectName, Platform, PlatformWorkerId):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["CHECK_PLATFORM_WORKER_ID_EXISTENCE_FOR_PROJECT"],
                                        { "ProjectName": ProjectName, "Platform": Platform, "PlatformWorkerId": PlatformWorkerId })


class MTurkController:
    def __init__(self, duct):
        self.duct = duct

    async def get_credentials(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_GET_CREDENTIALS"], None)

    async def set_credentials(self, AccessKeyId, SecretAccessKey):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_SET_CREDENTIALS"],
                                        { "AccessKeyId": AccessKeyId, "SecretAccessKey": SecretAccessKey })

    async def clear_credentials(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_CLEAR_CREDENTIALS"], None)

    async def set_sandbox(self, Enabled):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_SET_SANDBOX"], { "Enabled": Enabled })

    async def get_hit_types(self, HITTypeIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_GET_HIT_TYPES"], { "HITTypeIds": HITTypeIds })

    async def create_hit_type(self, CreateHITTypeParams, HITTypeQualificationTypeId):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_CREATE_HIT_TYPE"],
                                        { "CreateHITTypeParams": CreateHITTypeParams,
                                          "HITTypeQualificationTypeId": HITTypeQualificationTypeId })

    async def create_hits_with_hit_type(self, ProjectName, NumHITs, CreateHITsWithHITTypeParams):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_CREATE_HITS_WITH_HIT_TYPE"], 
                                        { "ProjectName": ProjectName, "NumHITs": NumHITs,
                                          "CreateHITsWithHITTypeParams": CreateHITsWithHITTypeParams })

    async def list_qualifications(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_LIST_QUALIFICATIONS"], None)

    async def list_hits(self, Cached):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_LIST_HITS"], { "Cached": Cached })

    async def list_hits_for_hit_type(self, HITTypeId=None, Cached=True):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_LIST_HITS_FOR_HIT_TYPE"],
                                        { "HITTypeId": HITTypeId, "Cached": Cached })

    async def expire_hits(self, HITIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_EXPIRE_HITS"], { "HITIds": HITIds })

    async def delete_hits(self, HITIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_DELETE_HITS"], { "HITIds": HITIds })

    async def create_qualification(self, QualificationTypeParams):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_CREATE_QUALIFICATION"],
                                        { "QualificationTypeParams": QualificationTypeParams })

    async def associate_qualifications_with_workers(self, QualificationTypeId, WorkerIds, IntegerValue, SendNotification):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_ASSOCIATE_QUALIFICATIONS_WITH_WORKERS"],
                                        { "QualificationTypeId": QualificationTypeId, "WorkerIds": WorkerIds, "IntegerValue": IntegerValue, "SendNotification": SendNotification })

    async def list_workers(self):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["LIST_WORKERS"], { "Platform": "MTurk" })

    async def list_workers_with_qualification_type(self, QualificationTypeId):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_LIST_WORKERS_WITH_QUALIFICATION_TYPE"],
                                        { "QualificationTypeId": QualificationTypeId })

    async def delete_qualifications(self, QualificationTypeIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_DELETE_QUALIFICATIONS"],
                                        { "QualificationTypeIds": QualificationTypeIds })

    async def list_assignments(self, Cached):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_LIST_ASSIGNMENTS"], { "Cached": Cached })

    async def list_assignments_for_hits(self, HITIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_LIST_ASSIGNMENTS_FOR_HITS"], { "HITIds": HITIds })

    async def approve_assignments(self, AssignmentIds, RequesterFeedback):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_APPROVE_ASSIGNMENTS"],
                                        { "AssignmentIds": AssignmentIds, "RequesterFeedback": RequesterFeedback })

    async def reject_assignments(self, AssignmentIds, RequesterFeedback):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_REJECT_ASSIGNMENTS"],
                                        { "AssignmentIds": AssignmentIds, "RequesterFeedback": RequesterFeedback })

    async def get_assignments(self, AssignmentIds):
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT["MTURK_GET_ASSIGNMENTS"], { "AssignmentIds": AssignmentIds })

