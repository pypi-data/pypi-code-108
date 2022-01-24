# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants definition."""

from sparkmagic.utils import constants

CREDENTIALS_resource = "https://dev.azuresynapse.net/"

SESSION_STATUS_STARTING = "starting"
SESSION_STATUS_STARTED = "started"
SESSION_STATUS_BUSY = "busy"
SESSION_STATUS_IDLE = "idle"
SESSION_STATUS_DEAD = "dead"
SESSION_STATUS_TIMEOUT = "timeout"
SESSION_STATUS_STOPPED = "stopped"


SESSION_KIND_PYSPARK = constants.SESSION_KIND_PYSPARK
SESSION_KIND_SPARK = constants.SESSION_KIND_SPARK
SESSION_KIND_CSHARP = "csharp"
SESSION_KIND_SQL = "sql"
SESSION_KINDS_SUPPORTED = [SESSION_KIND_SPARK, SESSION_KIND_PYSPARK, SESSION_KIND_CSHARP, SESSION_KIND_SQL]

US_GOV_CLOUD = ['usgovvirginia', 'usgoviowa', 'usgovtexas', 'usgovarizona', 'usdodeast', 'usdodcentral']
MOONCAKE_CLOUD = ['chinaeast', 'chinaeast2', 'chinanorth', 'chinanorth2']
BLACKFOREST_CLOUD = ['germanycentral', 'germanynortheast']

LIVY_ENDPOINT_DNS = "dev.azuresynapse.net"
LIVY_ENDPOINT_DNS_USGOV = "dev.azuresynapse.usgovcloudapi.net"
LIVY_ENDPOINT_DNS_MOONCAKE = "dev.azuresynapse.azure.cn"
LIVY_ENDPOINT_DNS_BLACKFOREST = "dev.azuresynapse.net"

SYNAPSE_UI_DNS = "web.azuresynapse.net"
SYNAPSE_UI_DNS_USGOV = "web.azuresynapse.usgovcloudapi.net"
SYNAPSE_UI_DNS_MOONCAKE = "web.azuresynapse.azure.cn"
SYNAPSE_UI_DNS_BLACKFOREST = "web.azuresynapse.net"

SPARK_UI_DNS = "ms.web.azuresynapse.net"
SPARK_UI_DNS_USGOV = "web.azuresynapse.usgovcloudapi.net"
SPARK_UI_DNS_MOONCAKE = "web.azuresynapse.azure.cn"
SPARK_UI_DNS_BLACKFOREST = "ms.web.azuresynapse.net"

LIVY_ENDPOINT_TEMPLATE = "https://{}.{}/livyApi/versions/2019-11-01-preview/sparkPools/{}"
SYNAPSE_UI_URL_TEMPLATE = "https://{}/monitoring/sparkapplication/{}?" \
                          "workspace=/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Synapse/workspaces/{}" \
                          "&livyId={}&sparkPoolName={}"
SPARK_UI_URL_TEMPLATE_UPDATED = "https://{}/sparkui/{}_{}/" \
                                "workspaces/{}/sparkpools/{}/sessions/{}/applications/{}/1/"
