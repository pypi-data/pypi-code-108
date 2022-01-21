import requests
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials

cred_dict = etld_lib_credentials.get_cred()
url = f"https://{cred_dict['api_fqdn_server']}/qps/rest/2.0/create/am/tag"

tags = {
"qetl-all-ec2": {"ruleText": "aws.ec2.accountId:*", "ruleType": "CLOUD_ASSET",  "provider": "EC2"},
"qetl-all-gcp": {"ruleText": "gcp.compute.instanceId:*", "ruleType": "CLOUD_ASSET",  "provider": "GCP"},
"qetl-all-azure": {"ruleText": "azure.vm.subscriptionId:*", "ruleType": "CLOUD_ASSET",  "provider": "AZURE"},
"qetl-all-hosts": {"ruleText": "return true;", "ruleType": "GROOVY",  "provider": "NONE"}
}

for tag in tags.keys():
    if 'NONE' in tags[tag]['provider']:
        provider_line = ""
    else:
        provider_line = f"<provider>{tags[tag]['provider']}</provider>"

    payload = f"<ServiceRequest><data><Tag><name>{tag}</name><ruleText>{tags[tag]['ruleText']}</ruleText>" \
              f"<ruleType>{tags[tag]['ruleType']}</ruleType>{provider_line}</Tag></data></ServiceRequest>"

    headers = {
      'Content-Type': 'text/xml',
      'X-Requested-With': 'QualysPostman',
      'Accept': 'application/json',
      'Authorization': cred_dict['authorization']
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)