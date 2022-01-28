from os import environ


def cluster_topic_map():
    cluster_0 = environ.get('NUBIUM_CLUSTER_0', '')
    cluster_1 = environ.get('NUBIUM_CLUSTER_1', '')
    cluster_2 = environ.get('NUBIUM_CLUSTER_2', '')
    test_cluster = environ.get('TEST_CLUSTER', '')
    dict_out = {
        "CampaignResponse_CampaignResponseFromEloqua_InquiriesRetriever_Timestamps": cluster_0,
        "CampaignResponse_CampaignResponseFromEloqua_InquiriesToCanon": cluster_0,
        "CampaignResponse_Canon_Input": cluster_0,
        "CampaignResponse_Canon": cluster_0,
        "CampaignResponse_CampaignResponseToSalesforce_CampaignMembersToUpsert_FirstTry": cluster_0,
        "CampaignResponse_CampaignResponseToSalesforce_CampaignMembersToUpsert_Retry1": cluster_0,
        "CampaignResponse_CampaignResponseToSalesforce_CampaignMembersToUpsert_Retry2": cluster_0,
        "CampaignResponse_CampaignResponseToSalesforce_CampaignMembersToUpsert_Retry3": cluster_0,
        "CampaignResponse_CampaignResponseToSalesforce_CampaignMembersToUpsert_Failure": cluster_0,
        "NubiumIntegrations_Eloqua_CdoUpdates_FirstTry": cluster_0,
        "NubiumIntegrations_Eloqua_CdoUpdates_Retry1": cluster_0,
        "NubiumIntegrations_Eloqua_CdoUpdates_Retry2": cluster_0,
        "NubiumIntegrations_Eloqua_CdoUpdates_Retry3": cluster_0,
        "NubiumIntegrations_Eloqua_CdoUpdates_Failure": cluster_0,
        "PeopleStream_PeopleStreamFromEloqua_ContactRetriever_Timestamps": cluster_0,
        "PeopleStream_PeopleStreamFromEloqua_ContactToCanon": cluster_0,
        "PeopleStream_PeopleStreamFromEloqua_UnsubscribeRetriever_Timestamps": cluster_0,
        "PeopleStream_PeopleStreamFromEloqua_UnsubscribeToCanon": cluster_0,
        "NubiumIntegrations_Eloqua_EbbController": cluster_0,
        "NubiumIntegrations_Eloqua_EbbWorkerTasks": cluster_0,
        "NubiumIntegrations_Vivastream_ContactsVivastreamRetriever_Timestamps": cluster_0,
        "NubiumIntegrations_UploadWizard_ContactsUploadsMembersRetriever_Timestamps": cluster_0,
        "NubiumIntegrations_RedHatTV_ContactsRedHatTVRetriever_Timestamps": cluster_0,
        "NubiumIntegrations_PartnerOutreach_ContactsActivitiesRetriever_Timestamps": cluster_0,

        "PeopleStream_Canon_Input": cluster_1,
        "PeopleStream_Canon": cluster_1,
        "PeopleStream_DataWashingMachine_ProcessedRecords": cluster_1,
        "PeopleStream_DataWashingMachine_Prewash": cluster_1,
        "PeopleStream_DataWashingMachine_DeptJobrolePersona": cluster_1,
        "PeopleStream_DataWashingMachine_AddressMsa": cluster_1,
        "PeopleStream_DataWashingMachine_Privacy": cluster_1,
        "NubiumIntegrations_Eloqua_ContactUpdates_FirstTry": cluster_1,
        "NubiumIntegrations_Eloqua_ContactUpdates_Retry1": cluster_1,
        "NubiumIntegrations_Eloqua_ContactUpdates_Retry2": cluster_1,
        "NubiumIntegrations_Eloqua_ContactUpdates_Retry3": cluster_1,
        "NubiumIntegrations_Eloqua_ContactUpdates_Failure": cluster_1,
        # TODO c1 PS3 - to sf filter and lead/contact updaters

        "NubiumIntegrations_Eloqua_FormPoster_FromDyFo_FirstTry": cluster_2,
        "NubiumIntegrations_Eloqua_FormPoster_FirstTry": cluster_2,
        "NubiumIntegrations_Eloqua_FormPoster_Retry1": cluster_2,
        "NubiumIntegrations_Eloqua_FormPoster_Retry2": cluster_2,
        "NubiumIntegrations_Eloqua_FormPoster_Retry3": cluster_2,
        "NubiumIntegrations_Eloqua_FormPoster_Failure": cluster_2,
        "NubiumIntegrations_Partner_BulkReceiver_Chunks": cluster_2,
        "NubiumIntegrations_Partner_BulkProcessor_Records": cluster_2,
        "NubiumIntegrations_DynamicForm_FormSubmissions": cluster_2,
        "NubiumIntegrations_DynamicForm_SpamFilter_CheckEmailAddress": cluster_2,
        "NubiumIntegrations_DynamicForm_SpamFilter_CheckVerifyId": cluster_2,
        "NubiumIntegrations_DynamicForm_SpamFilter_CheckSubmitId": cluster_2,
        "NubiumIntegrations_DynamicForm_SpamPosts": cluster_2,
        "NubiumIntegrations_DynamicForm_ErrorPosts": cluster_2,
        "PathFactory_PathFactory_DuplicatesFilter": cluster_2,
        "PathFactory_PathFactory_DuplicateClosedSessions": cluster_2,
        "PathFactory_PathFactory_ClosedSessions_FirstTry": cluster_2,
        "PathFactory_PathFactory_ClosedSessions_Retry1": cluster_2,
        "PathFactory_PathFactory_ClosedSessions_Retry2": cluster_2,
        "PathFactory_PathFactory_ClosedSessions_Failure": cluster_2,
        "NubiumIntegrations_Vivastream_CdoToFormTransform": cluster_2,
        "NubiumIntegrations_UploadWizard_CdoToFormTransform": cluster_2,
        "NubiumIntegrations_RedHatTV_CdoToFormTransform": cluster_2,
        "NubiumIntegrations_PartnerOutreach_Cdo2ProspectTransform": cluster_2,
        # TODO c2 PS3 - from sf lead/contact retrievers
    }
    if test_cluster:
        dict_out.update({f'{k}__TEST': test_cluster for k in dict_out})
    return dict_out
