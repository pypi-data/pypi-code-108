#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'ddadevops',
        version = '0.14.0',
        description = 'tools to support builds combining gopass, terraform, dda-pallet, aws & hetzner-cloud',
        long_description = '# dda-devops-build\n\n[![Slack](https://img.shields.io/badge/chat-clojurians-green.svg?style=flat)](https://clojurians.slack.com/messages/#dda-pallet/) | [<img src="https://meissa-gmbh.de/img/community/Mastodon_Logotype.svg" width=20 alt="team@social.meissa-gmbh.de"> team@social.meissa-gmbh.de](https://social.meissa-gmbh.de/@team) | [Website & Blog](https://domaindrivenarchitecture.org)\n\n![release prod](https://github.com/DomainDrivenArchitecture/dda-devops-build/workflows/release%20prod/badge.svg)\n\ndda-devops-build provide a environment to tie several DevOps tools together for easy interoperation. Supported tools are:\n* aws with\n  * simple api-key auth\n  * mfa & assume-role auth\n* hetzner with simple api-key auth\n* terraform v0.11, v0.12 supporting\n  * local file backends\n  * s3 backends\n* docker / dockerhub\n* user / team credentials managed by gopass\n* dda-pallet\n\n# Setup\n\nEnsure that yout python3 version is at least Python 3.7!\n\n```\nsudo apt install python3-pip\npip3 install pip3 --upgrade --user\npip3 install pybuilder ddadevops deprecation --user\nexport PATH=$PATH:~/.local/bin\n\n# in case of using terraform\npip3 install dda-python-terraform --user\n\n# in case of using AwsMixin\npip3 install boto3 --user\n\n# in case of using AwsMfaMixin\npip3 install boto3 mfa --user\n```\n\n# Example Build\n\nlets assume the following project structure\n\n```\nmy-project\n   | -> my-module\n   |       | -> build.py\n   |       | -> some-terraform.tf\n   | -> an-other-module\n   | -> target  (here will the build happen)\n   |       | -> ...\n```\n\n```\nfrom pybuilder.core import task, init\nfrom ddadevops import *\n\nname = \'my-project\'\nMODULE = \'my-module\'\nPROJECT_ROOT_PATH = \'..\'\n\nclass MyBuild(DevopsTerraformBuild):\n    pass\n\n\n@init\ndef initialize(project):\n    project.build_depends_on(\'ddadevops>=0.5.0\')\n    account_name = \'my-aws-account-name\'\n    account_id = \'my-aws-account-id\'\n    stage = \'my stage i.e. dev|test|prod\'\n    additional_vars = {\'var_to_use_insied_terraform\': \'...\'}\n    additional_var_files = [\'variable-\' + account_name + \'-\' + stage + \'.tfvars\']\n    config = create_devops_terraform_build_config(stage, PROJECT_ROOT_PATH,\n                                                  MODULE, additional_vars,\n                                                  additional_tfvar_files=additional_var_files)\n    build = MyBuild(project, config)\n    build.initialize_build_dir()\n\n\n@task\ndef plan(project):\n    build = get_devops_build(project)\n    build.plan()\n\n\n@task\ndef apply(project):\n    build = get_devops_build(project)\n    build.apply()\n\n@task\ndef destroy(project):\n    build = get_devops_build(project)\n    build.destroy()\n\n@task\ndef tf_import(project):\n    build = get_devops_build(project)\n    build.tf_import(\'aws_resource.choosen_name\', \'the_aws_id\')\n```\n\n## Feature aws-backend\n\nWill use a file `backend.dev.live.properties` where dev is the [account-name], live is the  [stage].\n\nthe backend.dev.live.properties file content:\n```\nkey = ".."\nregion = "the aws region"\nprofile = "the profile used for aws"\nbucket = "the s3 bucket name"\nkms_key_id = "the aws key id"\n```\n\nthe build.py file content:\n```\nclass MyBuild(AwsBackendPropertiesMixin, DevopsTerraformBuild):\n    pass\n\n\n@init\ndef initialize(project):\n    project.build_depends_on(\'ddadevops>=0.5.0\')\n    account_name = \'my-aws-account-name\'\n    account_id = \'my-aws-account-id\'\n    stage = \'my stage i.e. dev|test|prod\'\n    additional_vars = {}\n    config = create_devops_terraform_build_config(stage, PROJECT_ROOT_PATH,\n                                                  MODULE, additional_vars)\n    config = add_aws_backend_properties_mixin_config(config, account_name)\n    build = MyBuild(project, config)\n    build.initialize_build_dir()\n```\n\n## Feature aws-mfa-assume-role\n\nIn order to use aws assume role in combination with the mfa-tool (`pip install mfa`):\n\nthe build.py file content:\n```\nclass MyBuild(class MyBuild(AwsMfaMixin, DevopsTerraformBuild):\n    pass\n\n\n@init\ndef initialize(project):\n    project.build_depends_on(\'ddadevops>=0.5.0\')\n    account_name = \'my-aws-account-name\'\n    account_id = \'my-aws-account-id\'\n    stage = \'my stage i.e. dev|test|prod\'\n    additional_vars = {}\n    config = create_devops_terraform_build_config(stage, PROJECT_ROOT_PATH,\n                                                  MODULE, additional_vars)\n    config = add_aws_backend_properties_mixin_config(config, account_name)\n    config = add_aws_mfa_mixin_config(config, account_id, \'eu-central-1\',\n                                      mfa_role=\'my_developer_role\',\n                                      mfa_account_prefix=\'company-\',\n                                      mfa_login_account_suffix=\'users_are_defined_here\')\n    build = MyBuild(project, config)\n    build.initialize_build_dir()\n\n@task\ndef access(project):\n    build = get_devops_build(project)\n    build.get_mfa_session()\n```\n\n## Feature DdaDockerBuild\n\nThe docker build supports image building, tagging, testing and login to dockerhost.\nFor bash based builds we support often used script-parts as predefined functions [see install_functions.sh](src/main/resources/docker/image/resources/install_functions.sh).\n\nA full working example: [doc/example/50_docker_module](doc/example/50_docker_module)\n\n## Feature AwsRdsPgMixin\n\nThe AwsRdsPgMixin provides \n* execute_pg_rds_sql - function will optionally resolve dns-c-names for trusted ssl-handshakes\n* alter_db_user_password\n* add_new_user\n* deactivate_user\n\nthe build.py file content:\n```\nclass MyBuild(..., AwsRdsPgMixin):\n    pass\n\n\n@init\ndef initialize(project):\n    project.build_depends_on(\'ddadevops>=0.8.0\')\n\n    ...\n    config = add_aws_rds_pg_mixin_config(config,\n                                         stage + "-db.bcsimport.kauf." + account_name + ".breuni.de",\n                                         "kauf_bcsimport",\n                                         rds_resolve_dns=True,)\n    build = MyBuild(project, config)\n    build.initialize_build_dir()\n\n@task\ndef rotate_credentials_in(project):\n    build = get_devops_build(project)\n    build.alter_db_user_password(\'/postgres/support\')\n    build.alter_db_user_password(\'/postgres/superuser\')\n    build.add_new_user(\'/postgres/superuser\', \'/postgres/app\', \'pg_group_role\')\n\n\n@task\ndef rotate_credentials_out(project):\n    build = get_devops_build(project)\n    build.deactivate_user(\'/postgres/superuser\', \'old_user_name\')\n```\n\n# Releasing and updating\n## Publish snapshot\n\n1. every push will be published as dev-dependency\n\n## Release\n\n```\nadjust version no in build.py to release version no.\ngit commit -am "release"\ngit tag -am "release" [release version no]\ngit push --follow-tags\nincrease version no in build.py\ngit commit -am "version bump"\ngit push\npip3 install --upgrade --user ddadevops\n```\n\n# License\n\nCopyright © 2021 meissa GmbH\nLicensed under the [Apache License, Version 2.0](LICENSE) (the "License")\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Operating System :: POSIX :: Linux',
            'Operating System :: OS Independent',
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing'
        ],
        keywords = '',

        author = 'meissa GmbH',
        author_email = 'buero@meissa-gmbh.de',
        maintainer = '',
        maintainer_email = '',

        license = 'Apache Software License',

        url = 'https://github.com/DomainDrivenArchitecture/dda-devops-build',
        project_urls = {},

        scripts = [],
        packages = ['ddadevops'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {
            'ddadevops': ['LICENSE', 'src/main/resources/terraform/*', 'src/main/resources/docker/image/resources/*']
        },
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,<3.9,>=2.7',
        obsoletes = [],
    )
