# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['appcenter']

package_data = \
{'': ['*']}

install_requires = \
['azure-storage-blob>=2.1.0,<3.0.0',
 'deserialize>=1,<2',
 'requests>=2.22.0,<3.0.0',
 'tenacity>=6.2.0,<7.0.0']

setup_kwargs = {
    'name': 'appcenter',
    'version': '2.1.2',
    'description': 'A Python wrapper around the App Center REST API.',
    'long_description': 'This is a minimal Python wrapper around the App Center REST APIs to get you up and running. If you are looking for something more substantial, please refer to the REST API documentation: https://openapi.appcenter.ms/\n\nYou can install with `pip install appcenter`\n\n## Usage\n\n```python\n# 1. Import the library\nimport appcenter\n\n# 2. Create a new client\nclient = appcenter.AppCenterClient(access_token="abc123def456")\n\n# 3. Check some error groups\nstart = datetime.datetime.now() - datetime.timedelta(days=10)\nfor group in client.crashes.get_error_groups(owner_name="owner", app_name="myapp", start_time=start):\n    print(group.errorGroupId)\n    \n# 4. Get recent versions\nfor version in client.versions.all(owner_name="owner", app_name="myapp"):\n    print(version)\n    \n# 5. Create a new release\nclient.versions.upload_and_release(\n    owner_name="owner",\n    app_name="myapp",\n    version="0.1",\n    build_number="123",\n    binary_path="/path/to/some.ipa",\n    group_id="12345678-abcd-9012-efgh-345678901234",\n    release_notes="These are some release notes",\n    branch_name="test_branch",\n    commit_hash="1234567890123456789012345678901234567890",\n    commit_message="This is a commit message"\n)\n```\n\n## Contributing\n\nThis project welcomes contributions and suggestions.  Most contributions require you to agree to a\nContributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us\nthe rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.\n\nWhen you submit a pull request, a CLA bot will automatically determine whether you need to provide\na CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions\nprovided by the bot. You will only need to do this once across all repos using our CLA.\n\nThis project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).\nFor more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or\ncontact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.\n',
    'author': 'Dale Myers',
    'author_email': 'dalemy@microsoft.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Microsoft/appcenter-rest-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
