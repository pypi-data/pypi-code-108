# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.bing']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.0.8,<2.0.0', 'backoff>=1.10.0,<2.0.0', 'bingads==13.0.13']

setup_kwargs = {
    'name': 'arcane-bing',
    'version': '0.3.3',
    'description': 'Helpers to request bing API',
    'long_description': "# Arcane bing\n\nThis package is based on [bingads](https://docs.microsoft.com/en-us/advertising/guides/request-download-report?view=bingads-13).\n\n## Get Started\n\n```sh\npip install arcane-bing\n```\n\n## Example Usage\n\n### Reporting\n\n```python\nbing_client = Client(\n    credentials=Config.BING_ADS_CREDENTIALS,\n    secrets_bucket=Config.SECRETS_BUCKET,\n    refresh_token_location=Config.BING_ADS_REFRESH_TOKEN,\n    storage_client=storage_client\n)\n\nreporting_service_manager, reporting_service = bing_client.get_bing_ads_api_client()\n\nreport_request = build_campaigns_report(reporting_service, bing_account_id)\n\nresult_file_path = bing_client.submit_and_download(report_request, reporting_service_manager)\n```\n\n### Campaign Service\n\n:warning: For some API methods, you must provide the client's account id and the manager's customer id\n\n```python\nfrom arcane.bing import Client\nfrom arcane.bing.helpers import parse_webfault_errors, parse_bing_response\n\n\nbing_client = Client(\n    credentials=Config.BING_ADS_CREDENTIALS,\n    secrets_bucket=Config.SECRETS_BUCKET,\n    refresh_token_location=Config.BING_ADS_REFRESH_TOKEN,\n    storage_client=storage_client,\n    customer_id=CUSTOMER_ID,\n    account_id=ACCOUNT_ID\n)\n\ncampaign_service = bing_client.get_service_client(service_name='CampaignManagement')\n\ntry:\n    response = campaign_service.GetCampaignsByAccountId(AccountId=ACCOUNT_ID)\n    all_campaigns = parse_bing_response(response)['Campaign']\n    # do stuff with all_campaigns\nexcept WebFault as e:\n    bing_error = parse_webfault_errors(e)\n    # do stuff with bing_error\n```\n",
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
