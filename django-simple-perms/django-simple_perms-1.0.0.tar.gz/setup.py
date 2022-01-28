# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_perms']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.2,<4.0']

setup_kwargs = {
    'name': 'django-simple-perms',
    'version': '1.0.0',
    'description': 'A simple class based permission backend for django',
    'long_description': 'Really simple permission backend for django\n\nClass based, No database\n\nInspired by [django-permission](https://github.com/lambdalisue/django-permission)\n\nTested with Django 1.10 - python 3.5\n\n# Introduction\n\nThe app autodiscover perms.py module in your project\'s apps.\n\nThis modules should register PermissionLogic based class.\n\nWhen calling django\'s has_perm method, it will run the corresponding method name in your PermissionLogic class.\n\nSee usage section below for comprehensive example.\n\n# Usage\n\n*settings.py*\n\n```python\nINSTALLED_APPS = (\n  # ...\n  \'simple_perms\',  # Add simple_perms app to your INSTALLED_APPS\n  # ...\n)\n\nAUTHENTICATION_BACKENDS = (\n    \'simple_perms.PermissionBackend\',  # Add permission backend before django\'s one\n    \'django.contrib.auth.backends.ModelBackend\',\n)\n```\n\n*project_app/perms.py*\n\n```python\nfrom simple_perms import register, PermissionLogic\n\n\nclass ProjectLogic(PermissionLogic):\n\n    def add_project(self, user, project, perm):\n        return True\n\n    def change_project(self, user, project, perm):\n        return user.is_admin() or project.owner == user\n\n    delete_project = change_project\n\n    def default_permission(self, user, project, perm):\n      # Optional, default to global default permission, which default to False\n      return user.is_admin()\n\n\nregister(\'project_app\', ProjectLogic)\n```\n\n```python\nuser1.has_perm(\'project_app.add_project\')  # True\nuser1.has_perm(\'project_app.change_project\', user1_project)  # True\nuser1.has_perm(\'project_app.delete_project\', user1_project)  # True\nuser2.has_perm(\'project_app.change_project\', user1_project)  # False\nadmin.has_perm(\'project_app.change_project\', user1_project)  # True\n```\n\n# Default permission\n\nIf a checked permission doesn\'t exists in registered PermissionLogic based classe, the backend will run the default_permission method of this class. If no default_permission defined, it default to the global default permission which default to False.\n\n**Change global default permission**\n\n*settings.py*\n\n```python\nSIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION = \'path.to.custom_global_default_permission\'\n```\n\n*path/to.py*\n```python\ndef custom_global_default_permission(user, obj, perm):\n    return user.is_admin()\n```\n\nglobal_default_permission and default_permission have the same arguments as others permissions : `(user, obj, perm)`\n\n\n# Change autodiscovered module name\n\nsimple_perms autodiscover perms.py modules in every django\'s apps. You can change the module name to autodiscover using the SIMPLE_PERMS_MODULE_NAME setting :\n\n```python\nSIMPLE_PERMS_MODULE_NAME = \'permission\'\n```\n\n# Run tests\n\n```bash\npython runtests.py\n```\n\n# Helper for your tests\n\n```python\n\nfrom django.test import TestCase\nfrom simple_perms.helpers import AssertPermissions\n\n\nclass TestContractPermission(AssertPermissions, TestCase):\n    def setUp(self):\n        self.admin = UserFactory(role="admin")\n        self.contract = ContractFactory()\n\n    def test_permissions_for_admin(self):\n        permissions = [\n            { \'usr\': \'admin\', \'perm\': \'contracts.add\',    \'args\': (None,),           \'result\': True, },\n            { \'usr\': \'admin\', \'perm\': \'contracts.view\',   \'args\': (self.contract, ), \'result\': True, },\n            { \'usr\': \'admin\', \'perm\': \'contracts.change\', \'args\': (self.contract, ), \'result\': True, },\n        ]\n        self.assertPerms(permissions)\n```\n\nWhich fails:\n\n``` text\n======================================================================\nFAIL: test_permissions_for_admin (contracts.tests.perms.TestContractPermission)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File "/app/django/contracts/tests/perms.py", line 48, in test_permissions_of_admin\n    self.assertPerms(permissions)\n  File "/app/django/django-simple_perms/simple_perms/helpers.py", line 37, in assertPerms\n    raise e\n  File "/app/django/django-simple_perms/simple_perms/helpers.py", line 66, in _test_permission_\n    getattr(self, permission[\'usr\']).has_perm(permission[\'perm\'], *permission[\'args\'])\nAssertionError: (\'PERM ERROR admin contracts.add:  False is not true\', \'PERM ERROR admin contracts.view:  False is not true\', \'PERM ERROR admin contracts.change:  False is not true\')\n\n----------------------------------------------------------------------\n```\n',
    'author': 'Fabien MICHEL',
    'author_email': 'fabien.michel@hespul.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bitbucket.org/hespul/django-simple_perms',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
