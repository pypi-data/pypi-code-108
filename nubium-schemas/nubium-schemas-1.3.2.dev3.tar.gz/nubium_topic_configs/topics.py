from copy import deepcopy

def hrs_to_ms(hours):
    return 1000 * 60 * 60 * hours

def mb_to_bytes(mb):
    return 1024 * 1024 * mb

config_default = {
    "cleanup.policy": "delete",
    "retention.ms": hrs_to_ms(72),
    "segment.ms": hrs_to_ms(72),
    "segment.bytes": mb_to_bytes(100)
}

config_changelog = {
  **config_default,
  "cleanup.policy": "compact"
}

class TopicConfig:
    pass

class PrimaryTopicConfig(TopicConfig):
    def __init__(self, parts, rep_factor=3, config=None):
        self.partitions = parts
        self.replication_factor = rep_factor
        if not config:
          config = deepcopy(config_default)
        self.config = config


class InternalTopicConfig(TopicConfig):
    def __init__(self, config=None):
        if not config:
          config = deepcopy(config_default)
        self.config = config


class ChangelogTopicConfig(TopicConfig):
    def __init__(self, config=None):
        if not config:
          config = deepcopy(config_changelog)
        self.config = config


primary_topic_configs = {
    "PeopleStream": {
        "Canon": [
            PrimaryTopicConfig(parts=30),
            {"Input": PrimaryTopicConfig(parts=30)},
        ],
        "PeopleStreamFromEloqua": {
            "ContactRetriever": {"Timestamps": PrimaryTopicConfig(parts=1)},
            "ContactToCanon": PrimaryTopicConfig(parts=15),
            "UnsubscribeRetriever": {"Timestamps": PrimaryTopicConfig(parts=1)},
            "UnsubscribeToCanon": PrimaryTopicConfig(parts=3),
        },
        "DataWashingMachine": {
            "ProcessedRecords": PrimaryTopicConfig(parts=15),
            "Prewash": PrimaryTopicConfig(parts=15),
            "DeptJobrolePersona": PrimaryTopicConfig(parts=15),
            "AddressMsa": PrimaryTopicConfig(parts=15),
            "Privacy": PrimaryTopicConfig(parts=15),
        },
    },

    "CampaignResponse": {
        "Canon": [
            PrimaryTopicConfig(parts=9),
            {"Input": PrimaryTopicConfig(parts=9)},
        ],
        "CampaignResponseFromEloqua": {
            "InquiriesRetriever": {"Timestamps": PrimaryTopicConfig(parts=1)},
            "InquiriesToCanon": PrimaryTopicConfig(parts=6),
        },
        "CampaignResponseToSalesforce": {
            "CampaignMembersToUpsert": {
                "FirstTry": PrimaryTopicConfig(parts=9),
                "Retry1": PrimaryTopicConfig(parts=3),
                "Retry2": PrimaryTopicConfig(parts=1),
                "Retry3": PrimaryTopicConfig(parts=1),
                "Failure": PrimaryTopicConfig(parts=1),
            },
        },
    },

    "NubiumIntegrations": {
        "DynamicForm": {
            "FormSubmissions": PrimaryTopicConfig(parts=6),
            "SpamFilter": {
                "CheckEmailAddress": PrimaryTopicConfig(parts=6),
                "CheckVerifyId": PrimaryTopicConfig(parts=6),
                "CheckSubmitId": PrimaryTopicConfig(parts=6),
            },
            "SpamPosts": PrimaryTopicConfig(parts=3),
            "ErrorPosts": PrimaryTopicConfig(parts=1)
        },
        "Eloqua": {
            "EbbController": PrimaryTopicConfig(parts=3),
            "EbbWorkerTasks": PrimaryTopicConfig(parts=15),
            "FormPoster": {
                "FromDyFo": {
                    "FirstTry": PrimaryTopicConfig(parts=9)},
                "FirstTry": PrimaryTopicConfig(parts=9),
                "Retry1": PrimaryTopicConfig(parts=1),
                "Retry2": PrimaryTopicConfig(parts=1),
                "Retry3": PrimaryTopicConfig(parts=1),
                "Failure": PrimaryTopicConfig(parts=1),
            },
            "CdoUpdates": {
                "FirstTry": PrimaryTopicConfig(parts=9),
                "Retry1": PrimaryTopicConfig(parts=1),
                "Retry2": PrimaryTopicConfig(parts=1),
                "Retry3": PrimaryTopicConfig(parts=1),
                "Failure": PrimaryTopicConfig(parts=1),
            },
            "ContactUpdates": {
                "FirstTry": PrimaryTopicConfig(parts=30),
                "Retry1": PrimaryTopicConfig(parts=1),
                "Retry2": PrimaryTopicConfig(parts=1),
                "Retry3": PrimaryTopicConfig(parts=1),
                "Failure": PrimaryTopicConfig(parts=1),
            },
        },
        "Partner": {
            "BulkReceiver": {"Chunks": PrimaryTopicConfig(parts=1)},
            "BulkProcessor": {"Records": PrimaryTopicConfig(parts=6)},
        },
        "Vivastream": {
            "ContactsVivastreamRetriever": {"Timestamps": PrimaryTopicConfig(parts=1)},
            "CdoToFormTransform": PrimaryTopicConfig(parts=6),
        },
        "UploadWizard": {
            "ContactsUploadsMembersRetriever": {"Timestamps": PrimaryTopicConfig(parts=1)},
            "CdoToFormTransform": PrimaryTopicConfig(parts=6),
        },
        "RedHatTV": {
            "ContactsUploadsMembersRetriever": {"Timestamps": PrimaryTopicConfig(parts=1)},
            "CdoToFormTransform": PrimaryTopicConfig(parts=6),
        },
    },

    "PathFactory": {
        "PathFactory": {
            "DuplicatesFilter": PrimaryTopicConfig(parts=6),
            "DuplicateClosedSessions": PrimaryTopicConfig(parts=1),
            "ClosedSessions": {
                "FirstTry": PrimaryTopicConfig(parts=6),
                "Retry1": PrimaryTopicConfig(parts=1),
                "Retry2": PrimaryTopicConfig(parts=1),
                "Failure": PrimaryTopicConfig(parts=1),
            },
        },
    },
}

internal_topic_configs = {
    "PeopleStream": {
        "DataWashingMachine": {
            "Prewash": {"Internal_PeopleStream_DataWashingMachine_Prewasher": InternalTopicConfig()},
            "DeptJobrolePersona": {"Internal_PeopleStream_DataWashingMachine_DeptJobrolePersonaDeriver": InternalTopicConfig()},
            "AddressMsa": {"Internal_PeopleStream_DataWashingMachine_AddressMsa": InternalTopicConfig()},
            "ProcessedRecords": {"Internal_PeopleStream_PeopleStreamCanon_Aggregator": InternalTopicConfig()},
        },
        "Canon": {
            "Input": {"Internal_PeopleStream_PeopleStreamCanon_Aggregator": InternalTopicConfig()},
            "Internal_PeopleStream_PeopleStreamToEloqua_Filter": InternalTopicConfig(),
        },
    },

    "CampaignResponse": {
        "Canon": {
            "Input": {"Internal_CampaignResponse_CampaignResponseCanon_Aggregator": InternalTopicConfig()},
            "Internal_CampaignResponse_CampaignResponseToEloqua_Filter": InternalTopicConfig(),
            "Internal_CampaignResponse_CampaignResponseToSalesforce_Filter": InternalTopicConfig(),
        },
    },

    "NubiumIntegrations": {
        "DynamicForm": {
            "SpamFilter": {
                "CheckEmailAddress-GroupBy-SpamKeyedRecord.submission_id": InternalTopicConfig(),
                "CheckSubmitId-GroupBy-SpamKeyedRecord.submission_id": InternalTopicConfig(),
                "CheckVerifyId-GroupBy-SpamKeyedRecord.verification_id": InternalTopicConfig(),
            },
        },
        "Eloqua": {
            "EbbController": {
                "Internal_NubiumIntegrations_Eloqua_EbbController": InternalTopicConfig(),
                "Internal_NubiumIntegrations_Eloqua_EbbController-GroupBy-job_id": InternalTopicConfig(),
            },
        },
    },

    "PathFactory": {
        "Pathfactory": {
            "DuplicatesFilter": {
                "Internal_PathFactory_PathFactory_DuplicatesFilter": InternalTopicConfig(),
                "Internal_PathFactory_PathFactory_DuplicatesFilter-GroupBy-session_id_check": InternalTopicConfig(),
            },
        },
    },
}

internal_changelog_configs = {
    "PeopleStream": {
        "PeopleStreamCanon": {"Aggregator-people-stream-canon-changelog": ChangelogTopicConfig()},
        "DataWashingMachine": {"Prewasher-dwm_scrub_table-changelog": ChangelogTopicConfig()},
    },
    "CampaignResponse": {
        "CampaignResponseCanon": {"Aggregator-canon-changelog": ChangelogTopicConfig()}
    },

    "NubiumIntegrations": {
        "DynamicForm": {
            "SpamFilter-submit_table-changelog": ChangelogTopicConfig(),
            "SpamFilter-verify_table-changelog": ChangelogTopicConfig(),
        },
        "Eloqua": {
            "EbbController-bulk_job_data_table-changelog": ChangelogTopicConfig(),
            "EbbController-bulk_job_tasks_table-changelog": ChangelogTopicConfig(),
        },
    },

    "PathFactory": {
        "PathFactory": {"DuplicatesFilter-session_id_table-changelog": ChangelogTopicConfig()},
    },
}


def unpack_topic_dict(topic_dict, prev_layer=''):
    if isinstance(topic_dict, dict):
        return {
            name: config
            for key, value in topic_dict.items()
            for name, config in unpack_topic_dict(value, f'{prev_layer}_{key}' if prev_layer else key).items()
        }
    elif isinstance(topic_dict, list):
        return {
            name: config
            for item in topic_dict
            for name, config in unpack_topic_dict(item, prev_layer).items()
        }
    elif isinstance(topic_dict, TopicConfig):
       return {prev_layer: topic_dict}
    raise ValueError(f"unsupported type for topic_dict: {type(topic_dict)}")


primary_topics = unpack_topic_dict(primary_topic_configs)
internal_topics = unpack_topic_dict(internal_topic_configs)
changelog_topics = unpack_topic_dict(internal_changelog_configs)