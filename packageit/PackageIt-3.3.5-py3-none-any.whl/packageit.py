"""Managing the scaffolding and VCS for new and existing Python Packages.

Use a configuration (.ini) file to:

1. Create the "scaffolding" for a new package.

2. Examine existing scaffolding and add missing components like directories and files.

3. Version control

4. Apply PEP8 via Black

5. Update Git and GitHub

6. Upload to PyPi

7. PEP12 doc strings

8. Create a virtual environment for the project

9. Special thanks to Jacob Tomlinson.  This application is based on his article

`Creating an open source Python project from scratch
<https://jacobtomlinson.dev/series/creating-an-open-source-python-project-from-scratch/>`_.

10. Configurations through templates which are easier to change.

11.  Step-by-step procedure for beginners as well as connoisseurs.  Intention

was educational, but also functional.  This is a starting block to create

the initial structure that can be used to grow it bigger.

"""

import argparse
import datetime
import logging
import os
from pathlib import Path
import pkg_resources
import re
import requests
import shutil
import sys
import toml
from beetools import beeutils, beescript, beevenv
from beetools.beearchiver import Archiver, msg_error, msg_info, msg_milestone
import configparserext
from git import Repo, exc as git_exc

from gitignore_parser import parse_gitignore
from github import Github, GithubException as GH_Except
import json
from releaselogit import ReleaseLogIt
import semverit

# from packageit.PackageItException import OldVersionException
# from .ExceptionCodes import _status_codes

_PROJ_DESC = __doc__.split("\n")[0]
_PROJ_PATH = Path(__file__)
# _DESC = __doc__.split('\n')[0]
# _PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem
# _VERSION = '3.1.0'


class FileTemplate:
    src_pth: Path = None

    def create_from_template(self, p_templ_pth: Path, p_ow: bool = False):
        if not self.src_pth.exists() or p_ow:
            shutil.copy(p_templ_pth, self.src_pth)
        pass


class PackageIt:
    """Create new, build and install Python Packages from a template

    Use a configuration (.ini) file create the "scaffolding" for a new
    package.    The directories are created with all the necessary files.
    """

    def __init__(
        self,
        p_ini_pth,
        p_project_name,
        p_arc_extern_dir=None,
        p_token_dir=None,
        p_logger_name=False,
    ):
        """Initialize the class

        Parameters
        ----------
        p_ini_pth
            Path to the configuration ini file
        p_project_name
            Name of the package (module, lib or package) to create

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        if Path(p_ini_pth).exists() and p_project_name:
            self.success = True
            self.arc_extern_dir = p_arc_extern_dir
            # self.ini_def_pth = p_ini_pth
            self.logger_name = None
            self.logger = None
            if p_logger_name:
                self._logger_name = _PROJ_NAME
                self.logger = logging.getLogger(self._logger_name)

            self.packageit_ini_pth = p_ini_pth
            self.packageit_ini = configparserext.ConfigParserExt(
                inline_comment_prefixes="#"
            )
            self.packageit_ini.read([self.packageit_ini_pth])
            self.packageit_dir = _PROJ_PATH.parents[1]

            self.gh_repo = None
            self.gh_user = None
            self.github = None
            self.gh_dir = None
            self.ini_spec_pth = None
            self.origin = None

            self.project_anchor_dir = Path(
                self.packageit_ini.get(
                    "Detail", "{}ProjectAnchorDir".format(beeutils.get_os())
                )
            )
            self.project_root_dir = Path(
                self.project_anchor_dir, p_project_name
            ).resolve()
            self.project_src_dir = None
            self.project_dir = None

            self.project_author = self.packageit_ini.get("Detail", "Author")
            self.project_author_email = self.packageit_ini.get("Detail", "AuthorEmail")
            self.project_classifiers = GenClassifiers(
                _PROJ_NAME, self.packageit_ini_pth
            ).contents
            self.project_desc = None
            self.project_code = None
            self.project_docs_dir = None
            self.project_gh_bug_templ = self.packageit_ini.get("GitHub", "BugTemplate")
            self.project_gh_config_templ = self.packageit_ini.get(
                "GitHub", "ConfigTemplate"
            )
            self.project_gh_enable = self.packageit_ini.getboolean("GitHub", "Enable")
            self.project_gh_feature_templ = self.packageit_ini.get(
                "GitHub", "FeatureTemplate"
            )
            self.project_gh_issue_templ_dir = None
            self.project_gh_username = self.packageit_ini.get("GitHub", "UserName")
            self.project_gh_token = None
            self.project_gh_wf_dir = None
            self.project_git_enable = self.packageit_ini.getboolean("Git", "Enable")
            self.project_header_description = self.packageit_ini.get(
                "Detail", "HeaderDescription"
            )
            self.project_import_prod = [
                x[1]
                for x in self.packageit_ini.get(
                    "Import", "Prod", p_prefix=True, p_split=True
                )
            ]
            self.project_import_rewrite = self.packageit_ini.getboolean(
                "Import", "ReWrite"
            )
            self.project_import_test = [
                x[1]
                for x in self.packageit_ini.get(
                    "Import", "Test", p_prefix=True, p_split=True
                )
            ]
            self.project_ini = configparserext.ConfigParserExt(
                inline_comment_prefixes="#"
            )
            self.project_install_apps = [
                x[1]
                for x in self.packageit_ini.get("Install Apps", "App", p_prefix=True)
            ]
            self.project_long_description = self.packageit_ini.get(
                "Detail", "LongDescription"
            )
            self.project_name = p_project_name
            self.project_new = False
            self.project_packageit_config_dir = self.project_root_dir / ".packageit"
            self.project_packageit_ini_pth = Path(
                self.project_packageit_config_dir, "packageit.ini"
            )
            self.project_python_requires = self.packageit_ini.get(
                "Detail", "PythonRequires"
            )
            self.project_pypi_publishing = self.packageit_ini.get("PyPi", "Publishing")
            self.project_pypi_repository = self.packageit_ini.get("PyPi", "Repository")
            # self.project_readme_developing_enable = self.packageit_ini.getboolean(
            #     "ReadMe", "EnableDeveloping"
            # )
            # self.project_readme_releasing_enable = self.packageit_ini.getboolean(
            #     "ReadMe", "EnableReleasing"
            # )
            # self.project_readme_rst = None
            # self.project_readme_testing_enable = self.packageit_ini.getboolean(
            #     "ReadMe", "EnableTesting"
            # )
            self.project_readthedocs_enable = self.packageit_ini.getboolean(
                "ReadTheDocs", "Enable"
            )
            self.project_readthedocs_config_template = None
            self.project_readthedocs_newproject_template = None
            self.project_release = None
            self.project_setup_cfg = None
            self.project_setup_cfg_pth = self.project_root_dir / "setup.cfg"
            self.project_sphinx_enable = self.packageit_ini.getboolean(
                "Sphinx", "Enable"
            )
            self.project_sphinx_index_rst = None
            self.project_sphinx_source_dir = None
            self.project_sphinx_conf_py_inst = [
                x[1]
                for x in self.packageit_ini.get("Sphinx", "ConfPyInstr", p_prefix=True)
            ]
            self.project_sphinx_index_contents = [
                x[1]
                for x in self.packageit_ini.get("Sphinx", "AddContent", p_prefix=True)
            ]
            self.project_sphinx_index_sections = [
                x[1]
                for x in self.packageit_ini.get("Sphinx", "AddSection", p_prefix=True)
            ]
            self.project_tests_dir = self.project_root_dir / "tests"
            self.project_title = None
            self.project_type = self.packageit_ini.get("Detail", "Type")
            self.project_url = self.packageit_ini.get("Detail", "Url")
            self.project_venv_dir = None
            self.project_venv_enable = self.packageit_ini.getboolean("VEnv", "Enable")
            self.project_venv_name = self.project_name
            self.project_venv_root_dir = None
            self.project_venv_upgrade = None
            self.project_versionarchive_dir = self.project_root_dir / "VersionArchive"
            self.project_wheels = None
            self.project_version = semverit.SemVerIt(
                p_version=self.project_setup_cfg_pth
            )
            self.pypi_curr_token = None
            self.pypi_curr_token_name = None
            self.pypi_prod_token = None
            self.pypi_prod_token_name = None
            self.pypi_test_token = None
            self.pypi_test_token_name = None
            self.pyproject_toml_pth = self.project_root_dir / "pyproject.toml"
            self.git_repo = None
            self.templ_dir = self.packageit_dir / "templates"
            self.token_dir = p_token_dir
            self.verbose = self.packageit_ini.getboolean("General", "Verbose")

            if self.project_gh_enable:
                self.gh_dir = self.project_root_dir / ".github"
                self.project_gh_token = self.read_token(
                    self.packageit_ini.get("GitHub", "TokenFileName")
                )
                self.project_gh_wf_dir = self.gh_dir / "workflows"
                self.project_gh_issue_templ_dir = self.gh_dir / "ISSUE_TEMPLATE"
            # self.project_dir = Path(self.project_anchor_dir / self.project_name)
            if self.project_pypi_publishing == "GitHub":
                if self.packageit_ini.has_option("PyPi", "TokenFileNamePyPi"):
                    pypi_prod_token_fn = Path(
                        self.packageit_ini.get("PyPi", "TokenFileNamePyPi")
                    )
                    self.pypi_prod_token = self.read_token(pypi_prod_token_fn)
                    self.pypi_prod_token_name = pypi_prod_token_fn.stem
                if self.packageit_ini.has_option("PyPi", "TokenFileNameTestPyPi"):
                    pypi_test_token_fn = Path(
                        self.packageit_ini.get("PyPi", "TokenFileNameTestPyPi")
                    )
                    self.pypi_test_token = self.read_token(pypi_test_token_fn)
                    self.pypi_test_token_name = pypi_test_token_fn.stem
                if self.project_pypi_repository == "pypi":
                    self.pypi_curr_token = self.pypi_prod_token
                    self.pypi_curr_token_name = self.pypi_prod_token_name
                else:
                    self.pypi_curr_token = self.pypi_test_token
                    self.pypi_curr_token_name = self.pypi_test_token_name
            if self.project_readthedocs_enable:
                self.rtd_token = self.read_token(
                    self.packageit_ini.get("ReadTheDocs", "TokenFileName")
                )
                self.project_readthedocs_config_template = self.packageit_ini.get(
                    "ReadTheDocs", "ConfigTemplate"
                )
                self.project_readthedocs_newproject_template = self.packageit_ini.get(
                    "ReadTheDocs", "NewProjectTemplate"
                )
            if self.project_sphinx_enable:
                self.project_sphinx_docs_dir = self.project_root_dir / "docs"
                self.project_sphinx_source_dir = self.project_sphinx_docs_dir / "source"
                self.project_sphinx_conf_py_pth = (
                    self.project_sphinx_source_dir / "conf.py"
                )
                self.project_sphinx_index_rst_pth = (
                    self.project_sphinx_source_dir / "index.rst"
                )
            if self.project_venv_enable:
                self.project_venv_root_dir = Path(
                    self.packageit_ini.get(
                        "VEnv", "{}VEnvAnchorDir".format(beeutils.get_os())
                    )
                )
                self.project_venv_reinstall = self.packageit_ini.getboolean(
                    "VEnv", "ReinstallVenv"
                )
                self.project_venv_upgrade = self.packageit_ini.getboolean(
                    "VEnv", "Upgrade"
                )
            self.read_project_detail_specific()
            self.readme = ReadMe(self.project_root_dir)
        else:
            self.success = False
        pass

    def add_readme_badges(self):
        print(msg_milestone("Add badges..."))
        badge_detail = {
            "pypi": {
                "uri": """https://img.shields.io/{}/v/{}""".format(
                    self.project_pypi_repository, self.project_name
                ),
                "alt": "PyPi",
                "pos": 0,
                "target": "",
            },
            "ci": {
                "uri": """https://img.shields.io/github/workflow/status/{}/{}/CI""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "GitHub Actions - CI",
                "pos": 0,
                "target": """https://github.com/{}/{}/actions/workflows/ci.yaml""".format(
                    self.project_gh_username, self.project_name
                ),
            },
            "precommit": {
                "uri": """https://img.shields.io/github/workflow/status/{}/{}/Pre-Commit""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "GitHub Actions - Pre-Commit",
                "pos": 0,
                "target": """https://github.com/{}/{}/actions/workflows/pre-commit.yaml""".format(
                    self.project_gh_username, self.project_name
                ),
            },
            "codecov": {
                "uri": """https://img.shields.io/codecov/c/gh/{}/{}""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "CodeCov",
                "pos": 0,
                "target": """https://app.codecov.io/gh/{}/{}""".format(
                    self.project_gh_username, self.project_name
                ),
            },
            "githubsearch": {
                "uri": """https://img.shields.io/github/search/{}/{}/GitHub""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "GitHub Searches",
                "pos": 0,
                "target": "",
            },
            "pypidownload": {
                "uri": """https://img.shields.io/{}/dm/{}""".format(
                    self.project_pypi_repository, self.project_name
                ),
                "alt": "PyPI - Downloads",
                "pos": 0,
                "target": "",
            },
            "githubissues": {
                "uri": """https://img.shields.io/github/issues-raw/{}/{}""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "GitHub issues",
                "pos": 0,
                "target": "",
            },
            "license": {
                "uri": """https://img.shields.io/github/license/{}/{}""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "License",
                "pos": 0,
                "target": "",
            },
            "githubrelease": {
                "uri": """https://img.shields.io/github/v/release/{}/{}""".format(
                    self.project_gh_username, self.project_name
                ),
                "alt": "GitHub release (latest by date)",
                "pos": 0,
                "target": "",
            },
            "pypiversion": {
                "uri": """https://img.shields.io/{}/pyversions/{}""".format(
                    self.project_pypi_repository, self.project_name
                ),
                "alt": "PyPI - Python Version",
                "pos": 0,
                "target": "",
            },
            "pypiwheel": {
                "uri": """https://img.shields.io/{}/wheel/{}""".format(
                    self.project_pypi_repository, self.project_name
                ),
                "alt": "PyPI - Wheel",
                "pos": 0,
                "target": "",
            },
            "pypistatus": {
                "uri": """https://img.shields.io/{}/status/{}""".format(
                    self.project_pypi_repository, self.project_name
                ),
                "alt": "PyPI - Status",
                "pos": 0,
                "target": "",
            },
        }

        for badge in self.project_ini.get('Badges', 'Badge', True):
            if badge[1] == 'Yes':
                self.readme.add_directive_image(
                    p_uri=badge_detail[badge[0][5:]]["uri"],
                    p_alt=badge_detail[badge[0][5:]]["alt"],
                    p_pos=badge_detail[badge[0][5:]]["pos"],
                    p_target=badge_detail[badge[0][5:]]["target"],
                )
        pass

    def add_sphinx_index_contents(self):
        success = False
        if self.project_sphinx_enable:
            print(
                msg_milestone(
                    'Add "index contents": [{}]'.format(
                        ", ".join(self.project_sphinx_index_contents)
                    )
                )
            )
            for item in self.project_sphinx_index_contents:
                dest_pth = Path(self.project_sphinx_source_dir, "{}.rst".format(item))
                if not dest_pth.exists():
                    templ_pth = Path(self.templ_dir, "templ_{}.rst".format(item))
                    if templ_pth.exists():
                        shutil.copy(templ_pth, dest_pth)
                        if dest_pth.stem == "api":
                            dest_pth.write_text(
                                dest_pth.read_text().format(self.project_name.lower())
                            )
                    else:
                        rstbuilder = RSTBuilder(
                            p_pth=dest_pth, p_first_level_title=item.capitalize()
                        )
                        rstbuilder.write_text()
            self.project_sphinx_index_rst.add_toctree(
                self.project_sphinx_index_contents, p_maxdepth=2, p_caption="Contents"
            )
            # self.git_commit('Add Sphinx index content files')
            success = True
        return success

    def add_sphinx_index_sections(self):
        success = False
        print(
            msg_milestone(
                'Add "index sections": [{}]'.format(
                    ", ".join(self.project_sphinx_index_sections)
                )
            )
        )
        if self.project_sphinx_enable:
            for item in self.project_sphinx_index_sections:
                dest_pth = Path(self.project_sphinx_source_dir, "{}.rst".format(item))
                if not dest_pth.exists():
                    templ_pth = Path(self.templ_dir, "templ_{}.rst".format(item))
                    if templ_pth.exists():
                        shutil.copy(templ_pth, dest_pth)
                        item_contents = dest_pth.read_text().strip()
                    else:
                        item_contents = "Insert text in {}.rst".format(item)
                else:
                    item_contents = dest_pth.read_text().strip()
                self.project_sphinx_index_rst.add_second_level_title(item)
                self.project_sphinx_index_rst.add_code_block(item_contents)
                success = True
            # self.git_commit('Add Sphinx index sections')
        return success

    # def add_readme_developing(self):
    #     print(msg_milestone('Add README "Development" section...'))
    #     self.project_readme_rst.add_first_level_title("Developing")
    #     self.project_readme_rst.add_paragraph(
    #         """This project uses ``black`` to format code and ``flake8`` for
    #         linting. We also support ``pre-commit`` to ensure these have been
    #         run. To configure your local environment please install these
    #         development dependencies and set up the commit hooks."""
    #     )
    #     self.project_readme_rst.add_code_block(
    #         "$ pip install black flake8 pre-commit\n$ pre-commit install", "bash"
    #     )
    #     pass
    #
    # def add_readme_releasing(self):
    #     print(msg_milestone('Add README "Releasing" section...'))
    #     text = "# Set next version number\n"
    #     text += "export RELEASE = x.x.x\n\n"
    #     text += "# Create tags\n"
    #     text += 'git commit --allow -empty -m "Release $RELEASE"\n'
    #     text += 'git tag -a $RELEASE -m "Version $RELEASE"\n\n'
    #     text += "# Push\n"
    #     text += "git push upstream --tags"
    #
    #     self.project_readme_rst.add_first_level_title("Releasing")
    #     self.project_readme_rst.add_paragraph(
    #         "Releases are published automatically when a tag is pushed to GitHub."
    #     )
    #     self.project_readme_rst.add_code_block(text, "bash")
    #
    # def add_readme_testing(self):
    #     print(msg_milestone('Add README "Testing" section...'))
    #     templ_body_pth = self.project_dir / 'README_body.rst'
    #     if not self.project_ini.has_option('ReadMe', 'Body01'):
    #         templ_pth = self.project_dir / self.project_ini.has_option('ReadMe', 'DefaultTemplate')
    #         shutil.copy(templ_pth, templ_body_pth)
    #         self.project_ini.set('ReadMe', 'Body01', 'README_body.rst')
    #         with open(templ_body_pth, 'w') as fp:
    #             self.project_ini.write(fp)
    #     for part in self.project_ini.get('ReadMe', 'Body', p_prefix = True):
    #         self.project_readme_rst.add_formatted_text((self.project_dir / part).read_text())
    #     pass
    #
    def add_repo_files(self):
        include_lst = self.git_repo.untracked_files
        gitignore_pth = self.project_root_dir / '.gitignore'
        ignore_match = parse_gitignore(gitignore_pth)
        dir_contents = list(self.project_root_dir.glob('**/*'))
        # gitignore_parser excludes .gitignore & .github/* erroneously.  Add them manually
        for item in dir_contents:
            if (
                not ignore_match(item)
                or item.is_relative_to(self.project_gh_wf_dir)
                or item.is_relative_to(self.project_gh_issue_templ_dir)
            ):
                if item.is_file():
                    include_lst.append(str(item))
        return include_lst

    def add_forced_repo_files(self):
        include_lst = []
        forced_lst = [
            # self.project_root_dir / ".coveragerc",
            # self.project_root_dir / ".gitignore",
        ]
        for file in forced_lst:
            if file.exists():
                include_lst.append(str(file))
        return include_lst

    def cleanup(self):
        dest_pth = self.project_root_dir / "Dummy.txt"
        if dest_pth.is_file():
            self.git_repo.index.remove([str(dest_pth)])
            dest_pth.unlink()
            # self.git_commit('Remove "Dummy.txt" dummy file')

    def create__init__(self):
        """Create the __init__.py file."""
        dest_pth = self.project_dir / "__init__.py"
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        if not dest_pth.exists():
            shutil.copy(self.templ_dir / "__init__template.py", dest_pth)
            contents = dest_pth.read_text().format(self.project_name.lower())
            dest_pth.write_text(contents)
            # self.git_commit('Create __init__.py file')
        return dest_pth

    def create_conftest_py(self):
        """Create conftest helper from a template.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        dest_pth = self.project_tests_dir / "conftest.py"
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        if not dest_pth.is_file():
            shutil.copy(self.templ_dir / "conftest_template.py", dest_pth)
            contents = dest_pth.read_text().format(
                self.project_name.lower(), "{}", "{", "}"
            )
            res = dest_pth.write_text(contents)
            if res <= 0:
                dest_pth = None
        return dest_pth

    def create_coveragerc(self):
        dest_pth = self.project_root_dir / ".coveragerc"
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        omit_files_lst = [
            x[1] for x in self.packageit_ini.get("Coverage", "Omit", p_prefix=True)
        ]
        contents = "[run]\nomit = \n"
        for item in omit_files_lst:
            contents += "    {}\n".format(item)
        dest_pth.write_text(contents)
        # self.git_commit('Create coveragerc file')
        return dest_pth

    def create_git_ignore(self):
        """


        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        dest_pth = self.project_root_dir / ".gitignore"
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        if not dest_pth.is_file():
            shutil.copy(self.templ_dir / "templ_gitignore", dest_pth)

    def create_git_pre_commit_config_yaml(self):
        success = False
        dest_pth = None
        if self.project_git_enable:
            dest_pth = self.project_root_dir / ".pre-commit-config.yaml"
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                if not dest_pth.parent.is_dir():
                    dest_pth.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(
                    self.templ_dir / "git_pre-commit-config_template.yaml", dest_pth
                )
            # self.git_commit('Create {} file'.format(dest_pth))
            success = True
        if success:
            return dest_pth
        return success

    def create_github_bug_templ(self):
        dest_pth = None
        if self.project_gh_enable:
            dest_pth = self.project_gh_issue_templ_dir / "bug.md"
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                shutil.copy(self.templ_dir / self.project_gh_bug_templ, dest_pth)
                dest_pth.write_text(dest_pth.read_text().format(self.project_name))
            # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_github_ci_yaml(self):
        dest_pth = None
        if self.project_gh_enable:
            dest_pth = self.project_gh_wf_dir / "ci.yaml"
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                shutil.copy(self.templ_dir / "github_wf_ci_template.yaml", dest_pth)
            # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_github_config_templ(self):
        dest_pth = None
        if self.project_gh_enable:
            dest_pth = self.project_gh_issue_templ_dir / "config.yaml"
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                shutil.copy(self.templ_dir / self.project_gh_config_templ, dest_pth)
                dest_pth.write_text(dest_pth.read_text().format(self.project_name))
                # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_github_pre_commit_yaml(self):
        dest_pth = None
        if self.project_gh_enable:
            dest_pth = self.project_gh_wf_dir / "pre-commit.yaml"
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                if not dest_pth.parent.is_dir():
                    dest_pth.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(
                    self.templ_dir / "templ_github_wf_pre-commit.yaml", dest_pth
                )
                # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_github_release_yml(self):
        dest_pth = self.project_gh_wf_dir / "release.yml"
        if self.project_gh_enable and self.project_pypi_publishing == "GitHub":
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            prod_pypi_rep_url = """https://upload.pypi.org/legacy/"""
            test_pypi_rep_url = """https://test.pypi.org/legacy/"""
            prod_token_name = "PYPI_API_TOKEN"
            test_token_name = "TEST_PYPI_API_TOKEN"
            if self.project_pypi_repository == "pypi":
                pypi_rep_url = prod_pypi_rep_url
            else:
                pypi_rep_url = test_pypi_rep_url
            if not dest_pth.exists():
                if not dest_pth.parent.is_dir():
                    dest_pth.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(self.templ_dir / "github_wf_release_template.yml", dest_pth)
                contents = dest_pth.read_text().format(
                    "{0}", "{", "}", self.pypi_curr_token_name, pypi_rep_url
                )
            else:
                contents = dest_pth.read_text()
                if self.project_pypi_repository == "pypi":
                    src_url = test_pypi_rep_url
                    dest_url = prod_pypi_rep_url
                    src_token_name = ".{}".format(test_token_name)
                    dest_token_name = ".{}".format(prod_token_name)
                else:
                    src_url = prod_pypi_rep_url
                    dest_url = test_pypi_rep_url
                    src_token_name = ".{}".format(prod_token_name)
                    dest_token_name = ".{}".format(test_token_name)
                contents = contents.replace(src_url, dest_url)
                contents = contents.replace(src_token_name, dest_token_name)
            dest_pth.write_text(contents)
        else:
            if dest_pth.exists():
                dest_pth.unlink()
            dest_pth = None

        return dest_pth

    def create_github_feature_templ(self):
        dest_pth = None
        if self.project_gh_enable:
            dest_pth = self.project_gh_issue_templ_dir / "feature.md"
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                shutil.copy(self.templ_dir / self.project_gh_feature_templ, dest_pth)
                # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_license(self):
        """Create the LICENSE file


        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        dest_pth = self.project_root_dir / "LICENSE"
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        if dest_pth.exists():
            dest_pth.unlink()
        lic = GenLicense(_PROJ_NAME, "MITLicense", self.templ_dir).contents
        dest_pth.write_text(lic)
        # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_manifest(self):
        """Create the MANIFEST.in file."""
        dest_pth = self.project_root_dir / "MANIFEST.in"
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        if not dest_pth.exists():
            shutil.copy(self.templ_dir / "MANIFEST_template.in", dest_pth)
            contents = dest_pth.read_text().format(self.project_name.lower())
            dest_pth.write_text(contents)
            # self.git_commit('Create {} file'.format(dest_pth))
        return dest_pth

    def create_pyproject_toml(self):
        print(msg_milestone("Create {} file...".format(self.pyproject_toml_pth)))
        if not self.pyproject_toml_pth.exists():
            self.pyproject_toml_pth.touch()
            # self.git_commit('Create {} file'.format(self.pyproject_toml_pth.name))
        pyproject_toml = toml.load(self.pyproject_toml_pth)
        pyproject_toml["build-system"] = {
            "requires": ["setuptools", "wheel"],
            "build-backend": "setuptools.build_meta",
        }
        pyproject_toml["tool"] = {
            'black': {
                "skip-string-normalization": True,
                "extend-exclude": "/templates",
            }
        }
        self.pyproject_toml_pth.write_text(toml.dumps(pyproject_toml))
        pass

    def create_readme(self):
        """Create the default README


        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        print(msg_milestone('Create the "README"...'))
        body_pth = self.project_dir / 'README_body.rst'
        templ_body_pth = self.templ_dir / self.project_ini.get(
            'ReadMe', 'DefaultBodyTemplate'
        )
        self.readme.create_body_from_template(body_pth, templ_body_pth)
        if not self.project_title:
            self.project_title = "Multi source file project"
        if not self.project_desc:
            self.project_desc = (
                'This still has to be sorted. See "PackageIt.create_readme"'
            )
        self.add_readme_badges()
        self.readme.add_paragraph(self.project_title)
        self.readme.add_paragraph(self.project_desc, 1)
        self.readme.add_formatted_text(body_pth.read_text())
        self.readme.write_text()
        return self.readme.src_pth

    def create_readthedocs_project(self):
        response = None
        if self.project_readthedocs_enable and self.project_new:
            print(
                msg_milestone("Register {} at ReadTheDocs...".format(self.project_name))
            )
            url = "https://readthedocs.org/api/v3/projects/"
            headers = {"Authorization": f"token {self.rtd_token}"}
            proj_detail = (
                (self.templ_dir / self.project_readthedocs_newproject_template)
                .read_text()
                .format(
                    "{",
                    "}",
                    self.project_name,
                    "https://github.com/{}/{}".format(
                        self.project_gh_username, self.project_name
                    ),
                    self.project_name.lower(),
                )
            )
            # response = requests.get(url, headers = headers).json()
            # rtd_project_names = [x['name'] for x in response['results']]
            # if self.project_name in rtd_project_names and self.project_new:
            #     url = 'https://readthedocs.org/api/v3/projects/{}/'.format(self.project_name.lower())
            data = json.loads(proj_detail)
            response = requests.post(url, json=data, headers=headers)
        return response

    def create_readthedocs_yaml(self):
        """Create the ".readthedocs.yaml" file from a template.


        Some other variants like readthedocs.yaml, .readthedocs.yml, etc.
        are deprecated.

        Parameters
        ----------

        Returns
        -------

        See Also
        --------

        Notes
        -----

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent
        """

        dest_pth = self.project_root_dir / ".readthedocs.yaml"
        if self.project_readthedocs_enable:
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                shutil.copy(
                    self.templ_dir / self.project_readthedocs_config_template, dest_pth
                )
            requirements_docs_pth = (
                self.project_root_dir / "docs" / "requirements_docs.txt"
            )
            requirements_docs_pth.write_text("sphinx\nsphinx-autobuild\n")
            # self.git_commit('Create {} file'.format(dest_pth))
        else:
            if dest_pth.exists():
                dest_pth.unlink()
            dest_pth = None
        return dest_pth

    def create_release(self):
        self.project_release = ReleaseLogIt(self.project_packageit_config_dir)
        for rel_note in self.project_release:
            major = list(rel_note.keys())[0]
            minor = list(rel_note[major].keys())[0]
            patch = list(rel_note[major][minor].keys())[0]
            release_title = rel_note[major][minor][patch]["Title"]
            cor_title = self.make_version_title(
                "{}.{}.{}".format(major, minor, patch), "Version"
            )
            if release_title != cor_title:
                self.project_release.rel_notes[major][minor][patch]["Description"] = [
                    self.project_release.rel_notes[major][minor][patch]["Title"]
                ] + self.project_release.rel_notes[major][minor][patch]["Description"]
                self.project_release.rel_notes[major][minor][patch]["Title"] = cor_title

        self.project_release.write_toml()
        pass

    def create_requirements(self, p_filename, import_lst):
        dest_pth = self.project_root_dir / p_filename
        # print(msg_milestone('Create {} file...'.format(prod_dest_pth)))
        if self.project_import_rewrite:
            print(msg_milestone("Create {} file...").format(p_filename))
            contents = (
                "#===================================================================\n"
            )
            contents += "# This file is auto generated by PackageIt\n"
            contents += (
                "# Be careful to manually add modules as it might be over written.\n"
            )
            contents += "# Check the [Project Import][ReWrite] settings in:\n"
            contents += "# {} and\n".format(self.packageit_ini_pth)
            contents += "# {}\n".format(self.project_packageit_ini_pth)
            contents += (
                "#===================================================================\n"
            )
            if dest_pth.is_file():
                dest_pth.unlink()
            for item in import_lst:
                if item[0] == "pypi":
                    contents += "{}\n".format(item[1])
            dest_pth.write_text(contents)
            # self.git_commit('Create {} file'.format(prod_dest_pth))
        return dest_pth

    def create_scaffolding(self):
        """Create scaffolding for the project"""
        success = True
        print(msg_milestone("Create project scaffolding..."))
        # if not self.project_dir.exists():
        #     self.project_dir.mkdir(parents=True)
        if self.project_type == "Module":
            self.project_src_dir = self.project_root_dir / "src"
            self.project_dir = self.project_src_dir / self.project_name.lower()
        elif self.project_type == "Package":
            self.project_src_dir = self.project_root_dir / self.project_name.lower()
            self.project_dir = self.project_src_dir
        if not self.project_dir.exists():
            self.project_dir.mkdir(parents=True)
            self.project_new = True

        if not self.project_packageit_config_dir.exists():
            self.project_packageit_config_dir.mkdir(parents=True)
        if not self.project_sphinx_source_dir.exists():
            self.project_sphinx_source_dir.mkdir(parents=True)
        if not self.project_tests_dir.exists():
            self.project_tests_dir.mkdir(parents=True)
        if not self.project_versionarchive_dir.exists():
            self.project_versionarchive_dir.mkdir(parents=True)

        if self.project_gh_enable:
            if not self.project_gh_wf_dir.is_dir():
                self.project_gh_wf_dir.mkdir(parents=True, exist_ok=True)
            if not self.project_gh_issue_templ_dir.is_dir():
                self.project_gh_issue_templ_dir.mkdir(parents=True, exist_ok=True)

        if not self.project_packageit_ini_pth.exists():
            if not self.project_packageit_ini_pth.parents[0].exists():
                self.project_packageit_ini_pth.parents[0].mkdir(parents=True)
            self.make_project_specific_ini()

        # self.project_release = ReleaseLogIt(self.project_packageit_config_dir)
        return success

    def create_setup_cfg(self):
        print(
            msg_milestone("Create {} file...".format(self.project_setup_cfg_pth.name))
        )
        if not self.project_setup_cfg_pth.is_file():
            if not self.project_setup_cfg_pth.parent.is_dir():
                self.project_setup_cfg_pth.parent.mkdir(parents=True, exist_ok=True)
                self.project_setup_cfg_pth.touch()
        self.project_setup_cfg = configparserext.ConfigParserExt(
            inline_comment_prefixes="#"
        )
        self.project_setup_cfg.read([self.project_setup_cfg_pth])

        if not self.project_setup_cfg.has_section("metadata"):
            self.project_setup_cfg.add_section("metadata")
        metadata = [
            ["name", self.project_name],
            ["version", self.project_version.version],
            ["author", self.project_author],
            ["author_email", self.project_author_email],
            ["description", "Insert project description here"],
            ["long_description", "file: README.rst"],
            ["long_description_content_type", "text/x-rst"],
            ["classifiers", "\n{}".format("\n".join(self.project_classifiers))],
        ]
        for option in metadata:
            if not self.project_setup_cfg.has_option("metadata", option[0]):
                self.project_setup_cfg.set("metadata", option[0], option[1])

        if not self.project_setup_cfg.has_section("options"):
            self.project_setup_cfg.add_section("options")

        options = [
            [
                "install_requires",
                "\n{}".format("\n".join([x[1] for x in self.project_import_prod])),
            ],
            [
                "setup_requires",
                "\n{}".format("\n".join([x[1] for x in self.project_import_prod])),
            ],
            [
                "tests_require",
                "\n{}".format("\n".join([x[1] for x in self.project_import_test])),
            ],
            # ["python_requires", self.project_python_requires],
        ]
        options_packages_find = []
        if self.project_type == "Module":
            options.append(["package_dir", "\n=src"])
            if not self.project_setup_cfg.has_section("options.packages.find"):
                self.project_setup_cfg.add_section("options.packages.find")
                options_packages_find = [["where", "src"]]
        # if self.project_type == 'Package':
        options.append(["packages", "find:"])

        for option in options:
            if not self.project_setup_cfg.has_option("options", option[0]):
                self.project_setup_cfg.set("options", option[0], option[1])
        for option in options_packages_find:
            if not self.project_setup_cfg.has_option(
                "options.packages.find", option[0]
            ):
                self.project_setup_cfg.set(
                    "options.packages.find", option[0], option[1]
                )

        if not self.project_setup_cfg.has_section("flake8"):
            self.project_setup_cfg.add_section("flake8")
        for option in self.packageit_ini.options("flake8"):
            self.project_setup_cfg.set(
                "flake8", option, self.packageit_ini.get("flake8", option)
            )

        if not self.project_setup_cfg.has_section("tool:pytest"):
            self.project_setup_cfg.add_section("tool:pytest")
        for option in self.packageit_ini.options("tool:pytest"):
            self.project_setup_cfg.set(
                "tool:pytest", option, self.packageit_ini.get("tool:pytest", option)
            )

        with open(self.project_setup_cfg_pth, "w") as fp:
            self.project_setup_cfg.write(fp)
        return self.project_setup_cfg_pth

    def create_sphinx_conf_py(self):
        """Create the Sphinx conf.py"""
        if self.project_sphinx_enable and not self.project_sphinx_conf_py_pth.exists():
            print(
                msg_milestone(
                    "Create {} file...".format(self.project_sphinx_conf_py_pth)
                )
            )
            contents = "import sys\n"
            contents += "sys.path.insert(0, '{}')\n".format(
                str(self.project_src_dir).replace("\\", "\\\\")
            )
            contents += "project = '{}'\n".format(self.project_name)
            contents += "copyright = '{}, {}'\n".format(
                datetime.datetime.now().strftime("%Y"), self.project_author
            )
            contents += "author = '{}'\n".format(self.project_author)
            contents += "version = '{}'\n".format(self.project_version.maj)
            contents += "release = '0.0.1'\n"
            contents += """html_context = {}
                "display_github" : True,  # Integrate GitHub
                "github_user"    : "{}",  # Username
                "github_repo"    : "{}",  # Repo name
                "github_version" : "master",  # Version
                "conf_py_path"   : "/source/",  # Path in the checkout to the docs root
            {}\n""".format(
                "{", self.project_gh_username, self.project_name, "}"
            )

            for instr in self.project_sphinx_conf_py_inst:
                contents += "{}\n".format(instr)
            self.project_sphinx_conf_py_pth.write_text(contents)
        return self.project_sphinx_conf_py_pth

    def create_sphinx_docs(self):
        if self.project_sphinx_enable:
            print(msg_milestone("Build documentation by Sphinx..."))
            cmd = [
                self.project_root_dir.drive,
                "cd {}".format(self.project_root_dir),
                "sphinx-build -b html {} {}".format(
                    Path("docs", "source"), Path("docs", "build", "html")
                ),
            ]
            rc = beevenv.install_in(
                self.project_venv_root_dir, self.project_name, cmd, p_verbose=True
            )
            return rc

    def create_sphinx_index_rst(self):
        """Create the Sphinx conf.py"""
        if self.project_sphinx_enable:
            print(msg_milestone("Create index.rst..."))
            if self.project_sphinx_index_rst_pth.exists():
                self.project_sphinx_index_rst_pth.unlink()
            self.project_sphinx_index_rst = RSTBuilder(
                self.project_sphinx_index_rst_pth
            )
            self.project_sphinx_index_rst.add_comment(
                "======================================================"
            )
            self.project_sphinx_index_rst.add_comment(
                "This file is auto generated by PackageIt. Any changes"
            )
            self.project_sphinx_index_rst.add_comment("to it will be over written")
            self.project_sphinx_index_rst.add_comment(
                "======================================================"
            )
            self.project_sphinx_index_rst.add_first_level_title(self.project_name)
            for element in self.readme.elements:
                if self.readme.elements[element]["Type"] == "DirectiveImage":
                    self.project_sphinx_index_rst.add_element(
                        self.readme.elements[element]
                    )
            self.project_sphinx_index_rst.add_paragraph(self.project_header_description)
            self.project_sphinx_index_rst.add_paragraph(
                self.project_long_description, 1
            )
            self.add_sphinx_index_sections()
            self.add_sphinx_index_contents()
        return self.project_sphinx_index_rst

    def create_source_code_ini(self):
        """Modify ini template file for new module"""
        success = True
        if self.project_type == "Package":
            dest_pth = self.project_src_dir / "{}.ini".format(self.project_name)
            print(msg_milestone("Create {} file...".format(dest_pth.name)))
            if not dest_pth.is_file():
                shutil.copy(self.templ_dir / "templ_package.ini", dest_pth)
                contents = dest_pth.read_text().format(self.project_name)
                res = dest_pth.write_text(contents)
                # self.git_commit('Create {} file'.format(dest_pth))
                if res <= 0:
                    success = False
        return success

    def create_source_code_py(self):
        """Modify the template and copy it to the project folder


        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        dest_pth = self.project_dir / "{}.py".format(self.project_name.lower())
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        success = False
        dir_contents = list(self.project_dir.glob("*.py"))
        if not dir_contents:
            if self.project_type == "Module":
                shutil.copy(self.templ_dir / "templ_module.py", dest_pth)
            elif self.project_type == "Package":
                shutil.copy(self.templ_dir / "templ_package.py", dest_pth)
            contents = dest_pth.read_text().format(
                self.project_name,
                "{}",
                self.project_name.lower(),
                self.project_header_description,
                self.project_long_description,
            )
            dest_pth.write_text(contents)
        if self.get_title_and_desc(dest_pth):
            success = True
        return success

    def create_venv(self):
        """Create a virtual environment for the Application (Project)

        Create a virtual environment for the project.  If the [VEnv][ReinstallVenv]
        configuration setting is 'yes', the virtual environment will be
        installed or reinstalled regardless.  If [VEnv][ReinstallVenv] = 'No'
        then the virtual environment will only be installed if it does not
        exist.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        success = False
        if self.project_venv_enable:
            self.project_venv_dir = beevenv.get_dir(
                self.project_venv_root_dir, self.project_name
            )
            print(
                msg_milestone(
                    "Create virtual environment {}...".format(self.project_venv_dir)
                )
            )
            if self.project_venv_reinstall:
                beeutils.rm_tree(self.project_venv_dir)
            if not self.project_venv_dir.exists():
                beevenv.set_up(
                    self.project_venv_root_dir,
                    self.project_name,
                    p_package_list=self.project_import_test,
                )
            else:
                success = True
        return success

    def create_test_code(self):
        """Create test __ini__ procedure code from a template.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        success = True
        dest_pth = self.project_tests_dir / "test_{}.py".format(
            self.project_name.lower()
        )
        print(msg_milestone("Create {} file...".format(dest_pth.name)))
        if not dest_pth.is_file():
            if self.project_type == "Module":
                shutil.copy(self.templ_dir / "templ_test_module.py", dest_pth)
            elif self.project_type == "Package":
                shutil.copy(self.templ_dir / "templ_test_package.py", dest_pth)
            contents = dest_pth.read_text().format(
                self.project_name, self.project_name.lower()
            )
            res = dest_pth.write_text(contents)
            if res <= 0:
                success = False
        return success

    def do_pytest(self):
        """Install a Virtual Environment

        Install the required modules in the virtual environment if the
        [VEnv][ReinstallVenv] configuration setting is 'yes'.  If the
         upgrade switch is on [VEnv][Upgrade], the virtual environment will
         be installed or upgrade to the latest module versions.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        success = False
        if self.project_venv_enable:
            print(msg_milestone("Test code (pytest)..."))
            instructions = [
                self.project_venv_root_dir.drive,
                "cd {}".format(self.project_root_dir),
                "pytest",
            ]
            success = beevenv.install_in(
                self.project_venv_root_dir, self.project_name, instructions
            )
        return success

    def format_code(self):
        """Format code (PEP8)"""
        print(msg_milestone("Format code (PEP8)..."))
        cmd = [
            self.project_root_dir.drive,
            "cd {}".format(self.project_root_dir),
            "black --config {} {}".format(
                self.pyproject_toml_pth, str(self.project_root_dir / ".")
            ),
        ]
        rc = beevenv.install_in(
            self.project_venv_root_dir, self.project_name, cmd, p_verbose=True
        )
        return rc

    def get_github_repo_tags(self):
        print(msg_milestone("Get GitHub repo tags..."))
        tags = []
        for tag in self.gh_repo.get_tags():
            tags.append(tag.name)
        return tags

    @staticmethod
    def get_release_from_title(p_version_title):
        release = re.search(r"[0-9]\.[0-9]\.[0-9]", p_version_title)
        if release:
            return release[0]
        else:
            return None

    def get_pypi_project_version(self):
        if self.project_pypi_publishing != "No":
            if not self.project_new:
                print(
                    msg_milestone(f"Get details for {self.project_name} from PyPI...")
                )
                if self.project_pypi_repository == "pypi":
                    url = f"https://pypi.org/pypi/{self.project_name}/json"
                else:
                    url = f"https://test.pypi.org/pypi/{self.project_name}/json"
                response = requests.get(url)
                if response.status_code == 200:
                    version = response.json()["info"]["version"]
                else:
                    version = "0.0.0"
            else:
                version = self.project_version
        else:
            version = None
        return version

    def git_commit(self):
        """Commit files to Git"""
        success = False
        if self.project_git_enable:
            if self.project_new:
                commit_msg = "PackageIt initial project creation."
            else:
                commit_msg = "PackageIt automated update."
            # include_lst = self.add_repo_files() + self.add_forced_repo_files()
            print(msg_milestone("""Commit to Git - {}""".format(commit_msg)))
            # include_lst = self.add_repo_files() + self.add_forced_repo_files()
            self.git_repo.git.add(all=True)
            instructions = [
                self.project_root_dir.drive,
                "cd {}".format(self.project_root_dir),
                '''git commit -m "{}"'''.format(commit_msg),
            ]
            retry_cntr = 1
            retry_max = 2
            commit_success = False
            while not commit_success:
                try:
                    # The pre-commit must be executed in the new project environment and not in the current
                    # PackageIt environment and therefore the next few lines.
                    success = beevenv.install_in(
                        self.project_venv_root_dir,
                        self.project_name,
                        instructions,
                        p_verbose=True,
                    )
                    commit_success = True
                except git_exc.HookExecutionError as err:
                    if retry_cntr < retry_max:
                        print(
                            msg_info("Retry commit due to possible reformat condition.")
                        )
                        retry_cntr += 1
                    else:
                        print(msg_error(err))
                        print(msg_error("System will now terminate!"))
                        sys.exit()
        return success

    def git_push(self):
        """Submit files to Git"""
        success = False
        if self.project_git_enable:
            print(msg_milestone("Push to Git"))
            if not self.project_new:
                if self.project_version <= semverit.SemVerIt(
                    self.get_pypi_project_version()
                ):
                    release_toml_ver = semverit.SemVerIt(
                        self.project_release.latest_version()
                    )
                    gh_ver = semverit.SemVerIt(self.github_latest_tag())
                    pypi_ver = semverit.SemVerIt(self.get_pypi_project_version())
                    self.raise_exception_old_version(release_toml_ver, gh_ver, pypi_ver)
            try:
                self.git_repo.create_tag(
                    self.project_version.version,
                    message=f"Version {self.project_version}",
                )
            except git_exc.GitCommandError as err:
                print(msg_error(err.stderr))
            success = self.origin.push(all=True, set_upstream=True)
            success = self.origin.push(tags=True) and success
            self.git_repo.close()
        return success

    def github_format_titles(self):
        gh_releases = self.gh_repo.get_releases()
        for gh_release in gh_releases:
            cor_title = self.make_version_title(gh_release.tag_name, "Version")
            if gh_release.title != cor_title:
                body = "{}\n{}".format(gh_release.title, gh_release.body)
                gh_release.update_release(cor_title, body)
        return gh_releases

    def github_latest_tag(self):
        gh_tags = sorted(self.get_github_repo_tags())
        if gh_tags:
            return gh_tags[-1]
        return None

    def github_sync_release_notes(self):
        """Synchronise the release notes in .packageit/release.toml with
        the release notes in GitHub.  The release notes in GitHub is the
        master copy.

        :return: ReleaseLogIt
        """

        def add_gh_release_to_pi_releaselog(p_gh_rel):
            major, minor, patch = p_gh_rel.tag_name.split(".")
            rel_note = {
                major: {
                    minor: {
                        patch: {
                            "Title": p_gh_rel.tag_name,
                            "Description": p_gh_rel.body.split("\n"),
                        }
                    }
                }
            }
            self.project_release.add_release_note(rel_note)
            pass

        def add_pi_release_to_gh_releaselog(p_pi_rel):
            major, minor, patch = p_pi_rel.split(".")
            self.gh_repo.create_git_release(
                p_pi_rel,
                self.project_release.rel_notes[major][minor][patch]["Title"],
                "\n".join(
                    self.project_release.rel_notes[major][minor][patch]["Description"]
                ),
            )
            pass

        def gh_release_same_as_pi(p_gh_rel):
            rc = True
            major, minor, patch = p_gh_rel.tag_name.split(".")
            if (
                p_gh_rel.title
                != self.project_release.rel_notes[major][minor][patch]["Title"]
            ):
                rc = False
            if (
                p_gh_rel.body.split("\n")
                != self.project_release.rel_notes[major][minor][patch]["Description"]
            ):
                rc = False
            return rc

        def print_tags_and_exit(p_tag_black_list, p_gh_tags):
            print(
                msg_error(
                    "{} exist is in release.toml but not does not have a corresponding GitHub tag.".format(
                        ", ".join(p_tag_black_list)
                    )
                )
            )
            print(
                msg_error(
                    "Create the tag in GitHub/Git or remove the release note from release.tom. Sync again:"
                )
            )
            print(msg_error("Existing GitHub Tags: {}".format(", ".join(p_gh_tags))))
            print(msg_error("See also .packageit/release.toml"))
            pass

        def update_pi_releaselog(p_gh_rel):
            major, minor, patch = p_gh_rel.tag_name.split(".")
            self.project_release.rel_notes[major][minor][patch] = {
                "Description": p_gh_rel.body.split("\n"),
                "Title": p_gh_rel.title,
            }
            pass

        print(msg_milestone("Synchronise release notes..."))
        tag_black_list = []
        gh_rel_log = self.gh_repo.get_releases()
        gh_rel_log_list = [x.tag_name for x in gh_rel_log]
        pi_rel_log_list = [
            "{}.{}.{}".format(x[0], x[1], x[2]) for x in self.project_release.rel_list
        ]
        gh_tags = self.get_github_repo_tags()
        for gh_rel in gh_rel_log:
            if self.get_release_from_title(gh_rel.tag_name) in pi_rel_log_list:
                if not gh_release_same_as_pi(gh_rel):
                    update_pi_releaselog(gh_rel)
            else:
                add_gh_release_to_pi_releaselog(gh_rel)

        for pi_rel in pi_rel_log_list:
            if pi_rel not in gh_rel_log_list:
                if pi_rel in gh_tags:
                    add_pi_release_to_gh_releaselog(pi_rel)
                elif pi_rel != self.project_version.version:
                    tag_black_list.append(pi_rel)
        if tag_black_list:
            print_tags_and_exit(tag_black_list, gh_tags)

        return gh_rel_log_list or pi_rel_log_list

    def init_git(self):
        """Initialise Git"""
        success = False
        if self.project_git_enable:
            print(msg_milestone("Initialize Git..."))
            try:
                self.git_repo = Repo(self.project_root_dir)
            except git_exc.InvalidGitRepositoryError:
                self.git_repo = Repo.init(self.project_root_dir)
                with self.git_repo.config_writer() as config:
                    config.set_value("user", "email", self.project_author_email)
                    config.set_value("user", "name", self.project_author)
            if self.git_repo:
                # self.git_commit('Initialize Git')
                success = True
        return success

    def init_github(self):
        success = False
        if self.project_git_enable and self.project_gh_enable:
            print(msg_milestone("Initialize GitHub..."))
            self.github = Github(login_or_token=self.project_gh_token)
            if not self.project_gh_wf_dir.is_dir():
                self.gh_dir.mkdir(parents=True, exist_ok=True)
            if not self.project_gh_issue_templ_dir.is_dir():
                self.project_gh_issue_templ_dir.mkdir(parents=True, exist_ok=True)
            if self.github:
                success = True
        return success

    def init_github_repo(self):
        success = False
        if self.github:
            print(
                msg_milestone(
                    "Create GitHub {} repository...".format(self.project_name)
                )
            )
            self.gh_user = self.github.get_user()
            try:
                self.gh_repo = self.gh_user.create_repo(self.project_name)
                if self.pypi_prod_token_name:
                    self.gh_repo.create_secret(
                        self.pypi_prod_token_name, self.pypi_prod_token
                    )
                if self.pypi_test_token_name:
                    self.gh_repo.create_secret(
                        self.pypi_test_token_name, self.pypi_test_token
                    )
            except GH_Except as err:
                if err.status == 422:  # GitHub repo already exist
                    self.gh_repo = self.gh_user.get_repo(self.project_name)
                    pass
                else:
                    print(msg_error(err))
            if self.gh_repo:
                success = True
        return success

    def init_github_master_branch(self):
        success = False
        if self.gh_repo:
            print(
                msg_milestone(
                    'Initialize GitHub {} and create "master" branch...'.format(
                        self.project_name
                    )
                )
            )
            try:
                self.gh_repo.create_file(
                    "Dummy.txt",
                    "Initiate master branch",
                    'This file is created to initiate the "master branch" an will be deleted.\n',
                    "master",
                )
                success = True
            except GH_Except as err:
                if err.status == 404:
                    # 404 = non-existing object is requested.  This error only
                    # occur when running pytest. Cannot be recreated in normal
                    # operations and are therefore ignored.
                    success = True
                elif err.status == 422:
                    success = True
                else:
                    print(
                        msg_error(
                            "{} - {}\nSystem terminated.".format(
                                err.status, err.data["message"]
                            )
                        )
                    )
                    sys.exit()
        return success

    def install_editable_package(self):
        """Install a Virtual Environment

        Install the required modules in the virtual environment if the
        [VEnv][ReinstallVenv] configuration setting is 'yes'.  If the
         upgrade switch is on [VEnv][Upgrade], the virtual environment will
         be installed or upgrade to the latest module versions.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        success = False
        if self.project_venv_enable:
            print(msg_milestone("Install editable package..."))
            instructions = [
                "{}".format(self.project_root_dir.drive),
                "cd {}".format(self.project_root_dir),
                "pip install -e .",
            ]
            success = beevenv.install_in(
                self.project_venv_root_dir, self.project_name, instructions
            )
        return success

    def install_prereq_apps_in_venv(self):
        """Install a Virtual Environment

        Install the required modules in the virtual environment if the
        [VEnv][ReinstallVenv] configuration setting is 'yes'.  If the
         upgrade switch is on [VEnv][Upgrade], the virtual environment will
         be installed or upgrade to the latest module versions.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        success = False
        if self.project_venv_enable:
            print(msg_milestone("Install apps in virtual environment..."))
            instructions = [
                self.project_venv_root_dir.drive,
                "cd {}".format(self.project_root_dir),
            ]
            for app in self.project_install_apps:
                instructions.append(app)
            success = beevenv.install_in(
                self.project_venv_root_dir, self.project_name, instructions
            )
        return success

    def install_prereq_modules_in_venv(self):
        """Install a Virtual Environment

        Install the required modules in the virtual environment if the
        [VEnv][ReinstallVenv] configuration setting is 'yes'.  If the
         upgrade switch is on [VEnv][Upgrade], the virtual environment will
         be installed or upgrade to the latest module versions.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        imported_list = None
        if self.project_venv_enable:
            print(msg_milestone("Install modules in virtual environment..."))
            switches = ""
            instructions = [
                "{}".format(self.project_root_dir.drive),
                "cd {}".format(self.project_root_dir),
            ]
            # import_items = self.project_import_test + self.project_import_prod
            import_items = self.project_import_test
            imported_list = []
            for item in import_items:
                if item[0] == "pypi":
                    not_installed = False
                    try:
                        pkg_resources.get_distribution(item[1])
                    except pkg_resources.DistributionNotFound:
                        not_installed = True
                    if not_installed or self.project_venv_upgrade:
                        if self.project_venv_upgrade:
                            switches = '--upgrade'
                        if (
                            item[1] == "pip" or item[1] == "pip3"
                        ) and self.project_venv_upgrade:
                            instructions.append(
                                "python.exe -m pip install {} pip".format(switches)
                            )
                        else:
                            instructions.append(
                                "pip install {} {}".format(switches, item[1])
                            )
                        imported_list.append(item[1])
            if (
                beevenv.install_in(
                    self.project_venv_root_dir, self.project_name, instructions
                )
                != 0
            ):
                imported_list = []
        return imported_list

    def get_title_and_desc(self, p_project_pth):
        """Definition"""
        print(msg_milestone("Load {} ...".format(p_project_pth.name)))
        src = p_project_pth.read_text()
        res = re.search(r'"""[\s\S]*?"""', p_project_pth.read_text(), re.DOTALL)
        if not res:
            res = re.search(r"'''[\s\S]*?'''", p_project_pth.read_text(), re.DOTALL)
        doc_str = src[res.start() : res.end()].split('\n')
        for i, sep in enumerate(doc_str[1:]):
            if sep == '':
                break
        self.project_title = '\n'.join(doc_str[: i + 1]).strip()[3:]
        self.project_desc = '\n'.join(doc_str[i + 2 :])[:-3].strip()
        return self.project_title, self.project_desc

    def make_project_specific_ini(self) -> None:
        """Create a new project ini from a template.

        The new ini can be configured with specific parameters for the project.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        # templ_ini_pth = self.templ_dir / 'templ_project.ini'
        print(
            msg_milestone(
                "Create {} file...".format(self.project_packageit_ini_pth.name)
            )
        )
        shutil.copy(self.packageit_ini_pth, self.project_packageit_ini_pth)
        # self.git_commit('Create {} file'.format(self.project_packageit_ini_pth))
        pass

    @staticmethod
    def make_version_title(p_release, p_prefix=""):
        return "{} {}".format(p_prefix, p_release).strip()

    def make_wheels(self):
        """Create the wheels"""
        print(msg_milestone("Make {} wheels".format(self.project_name)))
        dist_dir = self.project_root_dir / "dist"
        if beeutils.get_os() == beeutils.WINDOWS:
            del_cmd = "del /Q {}".format(dist_dir)
        elif beeutils.get_os() == beeutils.LINUX:
            del_cmd = "rm {}".format(dist_dir)
        else:  # beeutils.get_os() == beeutils.MACOS:
            del_cmd = "rm {}".format(dist_dir)
        instructions = [
            "{}".format(self.project_root_dir.drive),
            "cd {}".format(self.project_root_dir),
            "{}".format(del_cmd),
            "python -m pip install build wheel",
            "python -m build",
        ]
        success = beevenv.install_in(
            self.project_venv_root_dir, self.project_name, instructions
        )
        self.project_wheels = list((self.project_root_dir / "dist").glob("*"))
        return success

    def marry_git_github(self):
        success = False
        if self.project_git_enable and self.project_gh_enable:
            print(
                msg_milestone("Marry Git and GitHub {} master branch").format(
                    self.project_name
                )
            )
            git_project_url = "{}/{}/{}.git".format(
                self.packageit_ini.get("GitHub", "Url").replace(" ", ""),
                self.packageit_ini.get("GitHub", "UserName"),
                self.project_name,
            )
            try:
                self.origin = self.git_repo.create_remote("origin", git_project_url)
            except git_exc.GitCommandError as err:
                if err.status == 3:  # Origin already exist
                    self.origin = self.git_repo.remote("origin")
                else:
                    print(msg_error(err))
                    sys.exit()
            # Assure we actually have data. fetch() returns useful information
            self.origin.fetch()
            try:
                # Create local branch "master" from remote "master"
                self.git_repo.create_head("master", self.origin.refs.master)
            except OSError as err:
                print(msg_info('Head "master" already exists.'))
                print(msg_info(err))
            # set local "master" to track remote "master
            self.git_repo.heads.master.set_tracking_branch(self.origin.refs.master)
            try:
                # checkout local "master" to working tree
                self.git_repo.heads.master.checkout()
            except git_exc.GitCommandError as err:
                if err.status == 1:  # Untracked files are not synced.
                    pass  # do nothing.  the files will be synced in self.git_submit
                else:
                    print(msg_error(err))
                    sys.exit()
            if self.origin and self.git_repo.heads.master:
                success = True
        return success

    @staticmethod
    def raise_exception_old_version(p_release_toml_ver, p_gh_ver, p_pypi_ver):
        data = [
            "The PyPI version is later or equal to any of the other versions.",
            "Any upload to PyPI will be unsuccessful.  The version in "
            + "release.toml or GitHub must be later than that of PyPI.",
            f"PyPI:\t\t\t{p_pypi_ver}",
            f"GitHub:\t\t\t{p_gh_ver}",
            f"release.toml:\t{p_release_toml_ver}",
        ]
        raise OldVersionException(_status_codes[1100], data)

    def read_project_detail_specific(self):
        """Read the specific project details from ini


        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        """
        success = False
        if self.project_packageit_ini_pth.exists():
            print(
                msg_milestone("Read {} configuration").format(
                    self.project_packageit_ini_pth.exists
                )
            )
            self.project_ini.read([self.project_packageit_ini_pth])
            if self.project_ini.has_option("Detail", "Author"):
                self.project_author = self.project_ini.get("Detail", "Author")
            if self.project_ini.has_option("Detail", "AuthorEmail"):
                self.project_author_email = self.project_ini.get(
                    "Detail", "AuthorEmail"
                )

            if self.project_ini.has_section("Classifiers"):
                self.project_classifiers = GenClassifiers(
                    _PROJ_NAME, self.project_packageit_ini_pth
                ).contents

            if self.project_ini.has_option("Git", "Enable"):
                self.project_git_enable = self.project_ini.getboolean("Git", "Enable")
            if self.project_ini.has_option("GitHub", "Enable"):
                self.project_gh_enable = self.project_ini.getboolean("GitHub", "Enable")
            if self.project_ini.has_option("GitHub", "UserName"):
                self.project_gh_username = self.project_ini.get("GitHub", "UserName")

            if self.project_ini.has_option("Detail", "HeaderDescription"):
                self.project_header_description = self.project_ini.get(
                    "Detail", "HeaderDescription"
                )

            if self.project_ini.has_option("Import", "ReWrite"):
                self.project_import_rewrite = self.project_ini.get("Import", "ReWrite")
            if self.project_ini.has_option("Import", "Prod001"):
                self.project_import_prod = [
                    x[1]
                    for x in self.project_ini.get(
                        "Import", "Prod", p_prefix=True, p_split=True
                    )
                ]
            if self.project_ini.has_option("Import", "Test001"):
                self.project_import_test = [
                    x[1]
                    for x in self.project_ini.get(
                        "Import", "Test", p_prefix=True, p_split=True
                    )
                ]

            if self.project_ini.has_option("Install Apps", "App01"):
                self.project_install_apps += [
                    x[1]
                    for x in self.project_ini.get("Install Apps", "App", p_prefix=True)
                ]

            if self.project_ini.has_option("Detail", "LongDescription"):
                self.project_long_description = self.project_ini.get(
                    "Detail", "LongDescription"
                )

            if self.project_ini.has_option("PyPi", "Publishing"):
                self.project_pypi_publishing = self.project_ini.get(
                    "PyPi", "Publishing"
                )
            if self.project_ini.has_option("PyPi", "Repository"):
                self.project_pypi_repository = self.project_ini.get(
                    "PyPi", "Repository"
                )
                if self.project_pypi_repository == "pypi":
                    pypi_token_fn = Path(
                        self.packageit_ini.get("PyPi", "TokenFileNamePyPi")
                    )
                else:
                    pypi_token_fn = Path(
                        self.packageit_ini.get("PyPi", "TokenFileNameTestPyPi")
                    )
                self.pypi_curr_token = self.read_token(pypi_token_fn)
                self.pypi_curr_token_name = pypi_token_fn.stem

            # if self.packageit_ini.has_option("ReadMe", "EnableDeveloping"):
            #     self.project_readme_developing_enable = self.packageit_ini.getboolean(
            #         "ReadMe", "EnableDeveloping"
            #     )
            # if self.packageit_ini.has_option("ReadMe", "EnableReleasing"):
            #     self.project_readme_releasing_enable = self.packageit_ini.getboolean(
            #         "ReadMe", "EnableReleasing"
            #     )
            # if self.packageit_ini.has_option("ReadMe", "EnableTesting"):
            #     self.project_readme_testing_enable = self.packageit_ini.getboolean(
            #         "ReadMe", "EnableTesting"
            #     )

            if self.project_ini.has_option("Sphinx", "Enable"):
                self.project_sphinx_enable = self.project_ini.getboolean(
                    "Sphinx", "Enable"
                )
            if self.project_ini.has_option("Sphinx", "ConfPyInstr001"):
                self.project_sphinx_conf_py_inst = [
                    x[1]
                    for x in self.project_ini.get(
                        "Sphinx", "ConfPyInstr", p_prefix=True
                    )
                ]

            if self.project_ini.has_option("Detail", "PythonRequires"):
                self.project_python_requires = self.project_ini.get(
                    "Detail", "PythonRequires"
                )
            if self.project_ini.has_option("Detail", "Url"):
                self.project_url = self.project_ini.get("Detail", "Url")

            if self.project_ini.has_option("VEnv", "Enable"):
                self.project_venv_enable = self.project_ini.has_option("VEnv", "Enable")
                self.project_venv_root_dir = Path(
                    self.project_ini.get(
                        "VEnv", "{}VEnvAnchorDir".format(beeutils.get_os())
                    )
                )
                if self.project_ini.has_option("VEnv", "ReinstallVenv"):
                    self.project_venv_reinstall = self.project_ini.getboolean(
                        "VEnv", "ReinstallVenv"
                    )
                if self.project_ini.has_option("VEnv", "Upgrade"):
                    self.project_venv_upgrade = self.project_ini.getboolean(
                        "VEnv", "Upgrade"
                    )
            success = True
        return success

    def read_token(self, p_token_filename):
        return (self.token_dir / p_token_filename).read_text().strip()

    def run(self):
        """Execution of the app"""
        self.create_scaffolding()
        self.zip_project()  # Zip before start of changes
        self.create_venv()
        self.create_git_ignore()
        self.init_github()
        self.init_github_repo()
        self.init_github_master_branch()
        self.init_git()
        self.marry_git_github()
        self.install_prereq_apps_in_venv()
        self.setup_sphinx()

        self.create_release()
        self.github_format_titles()
        self.github_sync_release_notes()
        self.create_sphinx_conf_py()
        self.create_source_code_py()
        self.create__init__()
        self.create_source_code_ini()
        self.create_license()
        self.create_test_code()
        self.create_conftest_py()
        self.create_pyproject_toml()
        self.create_github_ci_yaml()
        self.create_github_bug_templ()
        self.create_github_config_templ()
        self.create_github_feature_templ()
        self.create_setup_cfg()
        self.create_readme()
        self.create_manifest()
        self.create_requirements("requirements.txt", self.project_import_prod)
        self.create_requirements("requirements_test.txt", self.project_import_test)
        self.create_coveragerc()
        # self.add_badges()
        # self.create_readme()
        # self.project_readme_rst.write_text()
        self.create_sphinx_index_rst()
        self.project_sphinx_index_rst.write_text()
        self.create_sphinx_docs()
        self.format_code()
        self.create_github_release_yml()
        self.create_git_pre_commit_config_yaml()
        self.create_github_pre_commit_yaml()
        self.create_readthedocs_yaml()
        self.update_to_latest_version()
        # self.update_git_release()

        # self.cleanup() # See github issue #27
        self.install_editable_package()
        # self.do_pytest()
        self.git_commit()
        self.git_push()
        self.make_wheels()
        self.upload_to_pypi()
        self.git_repo.close()
        self.create_readthedocs_project()
        self.zip_project()  # Zip after changes
        pass

    def setup_sphinx(self):
        success = False
        if self.project_sphinx_enable and not self.project_sphinx_conf_py_pth.exists():
            print(msg_milestone("Setup Sphinx..."))
            instructions = [
                self.project_venv_root_dir.drive,
                "cd {}".format(self.project_root_dir),
            ]
            sphinx_cmd = "sphinx-quickstart "
            sphinx_cmd += "--sep "
            sphinx_cmd += "--project {} ".format(self.project_name)
            sphinx_cmd += '--author "{}" '.format(self.project_author)
            sphinx_cmd += "-v 1 -r 0 "
            sphinx_cmd += "--language en "
            sphinx_cmd += "--makefile "
            sphinx_cmd += "--batchfile "
            sphinx_cmd += "docs"
            instructions.append(sphinx_cmd)
            success = beevenv.install_in(
                self.project_venv_root_dir, self.project_name, instructions
            )
            self.project_sphinx_conf_py_pth.unlink()
        return success

    def update_to_latest_version(self):
        # if not self.project_new:
        release_toml_ver = semverit.SemVerIt(self.project_release.latest_version())
        gh_ver = semverit.SemVerIt(self.github_latest_tag())
        pypi_ver = semverit.SemVerIt(self.get_pypi_project_version())
        latest_ver = None
        if gh_ver <= pypi_ver and release_toml_ver <= pypi_ver and not self.project_new:
            self.raise_exception_old_version(release_toml_ver, gh_ver, pypi_ver)
        elif gh_ver >= release_toml_ver:
            latest_ver = gh_ver
        else:
            latest_ver = release_toml_ver
        self.project_setup_cfg.set("metadata", "version", str(latest_ver))
        with open(self.project_setup_cfg_pth, "w") as fp:
            self.project_setup_cfg.write(fp)
        self.project_version = latest_ver
        return latest_ver

    def upload_to_pypi(self):
        """Upload to PyPi"""
        success = False
        if (
            self.project_pypi_publishing == "Twine"
            or self.project_pypi_publishing == "Reahl"
        ):
            print(msg_milestone("Manual upload {} to PyPi".format(self.project_name)))
            cmd = [
                "{}".format(self.project_root_dir.drive),
                "cd {}".format(self.project_root_dir),
                "twine upload --repository {} --skip-existing dist/*".format(
                    self.project_pypi_repository
                ),
            ]
            success = beescript.exec_batch_in_session(cmd)
        elif self.project_pypi_publishing == "GitHub":
            print(msg_milestone("Github push {} to PyPi".format(self.project_name)))
            success = True
        else:
            print(msg_milestone("No publishing {} to PyPi".format(self.project_name)))
        return success

    def zip_project(self):
        print(msg_milestone("Archive {} files...").format(self.project_name))
        arc = Archiver(
            self.project_header_description,
            self.project_root_dir,
            p_app_ini_file_name=self.project_packageit_ini_pth,
            p_arc_extern_dir=self.arc_extern_dir,
        )
        return arc.arc_pth
        pass


class GenClassifiers:
    def __init__(self, p_parent_log_name, p_ini_pth, p_logger=False, p_verbose=True):
        self.success = True
        self.verbose = p_verbose
        self.log_name = None
        self.logger = None
        if p_logger:
            self.log_name = "{}.{}".format(p_parent_log_name, _PROJ_NAME)
            self.logger = logging.getLogger(self.log_name)
        self.contents = []
        self.dev_status = None
        self.ini = configparserext.ConfigParserExt(inline_comment_prefixes="#")
        self.ini_pth = p_ini_pth
        self.intended_audience = None
        self.license = None
        self.programming_language = None
        self.topic = None
        self.read_ini()
        pass

    def read_ini(self, p_ini_pth=None):
        self.contents = []
        if p_ini_pth:
            self.ini_pth = p_ini_pth
        self.ini.read([self.ini_pth])
        self.dev_status = self.ini.get("Classifiers", "DevStatus")
        self.contents.append(self.dev_status)
        self.intended_audience = [
            x[1] for x in self.ini.get("Classifiers", "IntendedAudience", p_prefix=True)
        ]
        self.contents += self.intended_audience
        self.topic = [x[1] for x in self.ini.get("Classifiers", "Topic", p_prefix=True)]
        self.contents += self.topic
        self.license = self.ini.get("Classifiers", "License")
        self.contents.append(self.license)
        self.programming_language = [
            x[1]
            for x in self.ini.get("Classifiers", "ProgrammingLanguage", p_prefix=True)
        ]
        self.contents += self.programming_language
        return self.contents


class GenSetUpPy:
    def __init__(
        self,
        p_setup_py_dir,
        p_name=None,
        p_version=None,
        p_author=None,
        p_author_email=None,
        p_classifiers=None,
        p_description=None,
        # p_long_description = None,
        p_package_dir=None,
        p_packages=None,
        p_python_requires=None,
        # p_install_requires = None
    ):
        self.pth = p_setup_py_dir / "setup.py"
        self.exist = self.exists()
        self.name = p_name
        self.version = p_version
        self.author = p_author
        self.author_email = p_author_email
        self.description = p_description
        self.classifiers = p_classifiers
        self.long_description = None
        self.long_description_content_type = """'text/x-rst',\n"""
        self.packages_dir = p_package_dir
        self.packages = p_packages
        self.python_requires = p_python_requires
        self.install_requires = None
        pass

    def exists(self):
        self.exist = self.pth.exists()
        return self.exist

    def write_text(self):
        contents = """\nimport setuptools\n\n\n"""
        contents += """with open('README.rst', 'r') as fh:\n"""
        contents += """    long_description = fh.read()\n"""
        contents += """with open('requirements.txt', 'r') as fh:\n"""
        contents += """    requirements = [line.strip() for line in fh]\n\n\n"""
        contents += """setuptools.setup(\n"""
        contents += """    name = '{}',\n""".format(self.name)
        contents += """    version = '{}',\n""".format(self.version)
        contents += """    author = '{}',\n""".format(self.author)
        contents += """    author_email = '{}',\n""".format(self.author_email)
        contents += """    description = '{}',\n""".format(self.description)
        contents += """    long_description = long_description,\n"""
        contents += """    long_description_content_type = 'text/x-rst',\n"""
        contents += """    classifiers = [\n        '{}'\n    ],\n""".format(
            """',\n        '""".join(self.classifiers)
        )
        if self.packages_dir:
            contents += """    package_dir = {},\n""".format(self.packages_dir)
        contents += """    packages = {},\n""".format(self.packages)
        contents += """    python_requires = '{}',\n""".format(self.python_requires)
        contents += """    install_requires = requirements\n"""
        contents += ")\n"
        self.pth.write_text(contents)
        self.exist = True


class GenLicense:
    def __init__(
        self, p_parent_log_name, p_type, p_templ_pth, p_logger=False, p_verbose=True
    ):
        """Initialize the class"""
        self.success = True
        self.verbose = p_verbose
        self.log_name = None
        self.logger = None
        if p_logger:
            self.log_name = "{}.{}".format(p_parent_log_name, _PROJ_NAME)
            self.logger = logging.getLogger(self.log_name)
        self.contents = None
        self.templ_prefix = "templ_lic"
        self.templ_pth = p_templ_pth
        self.type = p_type
        self.lic_types = []
        self.lic_pth = (
            self.templ_pth / "{}_{}".format(self.templ_prefix, self.type)
        ).with_suffix(".txt")
        self.get_lic_types()
        if self.verify_lic_type():
            self.get_type_text()
        pass

    def get_lic_types(self):
        self.lic_types = []
        for filename in self.templ_pth.glob("{}*.txt".format(self.templ_prefix)):
            self.lic_types.append(str(filename.stem)[len(self.templ_prefix) + 1 :])
        return self.lic_types

    def get_type_text(self):
        self.contents = self.lic_pth.read_text()
        return self.contents

    def verify_lic_type(self):
        success = False
        if self.type in self.lic_types:
            success = True
        return success


class RSTBuilder(FileTemplate):
    """Build a  reStructuredText (RST) file.

    The file will be rebuilt everytime i.e. it will be deleted and recreated
    from scratch according to the elements of the object.
    """

    def __init__(
        self,
        p_pth=None,
        p_first_level_title=None,
        p_tab_len=4,
        p_verbose=True,
        p_parent_log_name=None,
    ):
        """Initialize the class"""
        self.success = True
        self.loger_name = None
        self.logger = None
        if p_parent_log_name:
            self.loger_name = "{}.{}".format(p_parent_log_name, 'RSTBuilder')
            self.logger = logging.getLogger(self.loger_name)
        self.contents = ""
        self.curr_pos = 0
        self.element_cntr = 0
        self.elements = {}
        self.src_pth = p_pth
        if p_first_level_title:
            self.add_first_level_title(p_first_level_title)
        self.tab_len = p_tab_len
        self.verbose = p_verbose

    def __iter__(self):
        self.curr_pos = 0
        return self

    def __next__(self):
        if self.curr_pos < self.element_cntr:
            element = self.elements[self.curr_pos]
            self.curr_pos += 1
            return element
        else:
            raise StopIteration

    def add_code_block(self, p_text, p_lang="bash", p_pos=None):
        """Add a code-block to the rst text.

        Add a code-block to the rst text by specifying the language and the
        position in teh text.

        Parameters
        ----------
        p_text : str
            The code-block text to add
        p_lang : str, default = ''
            Language to use to format the code-block
        p_pos : int, default = None
            Specify the position where to add the code-block to the text.
            ``None`` will add it at the end of the current text.

        Returns
        -------
        pos : int
            The position the code-block was inserted in the text.

        See Also
        --------
        `Code blocks with syntax highlighting
        <https://docs.typo3.org/m/typo3/docs-how-to-document/master/en-us/WritingReST/Codeblocks.html>`_.

        Notes
        -----

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent
        """
        text = ".. code-block:: {}\n\n{}{}\n".format(
            p_lang,
            self._make_indent(1),
            p_text.replace("\n", "\n{}".format(self._make_indent(1))),
        )
        text += "\n"
        element = {"Type": "CodeBlock", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_comment(self, p_text, p_pos=None):
        """Method description"""
        text = p_text.strip().replace("\n", " ")
        while text.find("  ") >= 0:
            text = text.replace("  ", " ")
        text = ".. {}\n\n".format(text)
        element = {"Type": "Comment", "Text": text}
        pos = self._insert_at(element, p_pos)
        if pos > 0 and self.elements[pos - 1]["Type"] == "Comment":
            self.elements[pos - 1]["Text"] = self.elements[pos - 1]["Text"][:-1]
        return pos

    def add_directive_image(
        self,
        p_uri,
        p_align=None,
        p_alt=None,
        p_height=None,
        p_level=0,
        p_pos=None,
        p_scale=None,
        p_target=None,
        p_width=None,
    ):
        # ..image: : https: // img.shields.io / pypi / v / BEETest?style = plastic
        #     :alt: PyPI
        text = self._make_indent(p_level) + ".. image:: {}\n".format(p_uri)
        if p_align:
            text += self._make_indent(p_level + 1) + ":align: {}\n".format(p_align)
        if p_alt:
            text += self._make_indent(p_level + 1) + ":alt: {}\n".format(p_alt)
        if p_height:
            text += self._make_indent(p_level + 1) + ":height: {}\n".format(p_height)
        if p_scale:
            text += self._make_indent(p_level + 1) + ":scale: {}\n".format(p_scale)
        if p_target:
            text += self._make_indent(p_level + 1) + ":target: {}\n".format(p_target)
        if p_width:
            text += self._make_indent(p_level + 1) + ":width: {}\n".format(p_width)
        text += "\n"
        element = {"Type": "DirectiveImage", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_element(self, p_element, p_pos=None):
        return self._insert_at(p_element, p_pos)

    def add_first_level_title(self, p_text, p_pos=None):
        """Method description"""
        text = "{}\n{}\n{}\n".format(
            self._underline(p_text, "="), p_text, self._underline(p_text, "=")
        )
        text += "\n"
        element = {"Type": "FirstLevelTitle", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_fifth_level_title(self, p_text, p_pos=None):
        """Method description"""
        text = "{}\n{}\n".format(p_text, self._underline(p_text, "'"))
        text += "\n"
        element = {"Type": "FifthLevelTitle", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_formatted_text(self, p_text, p_pos=None):
        """Method description"""
        element = {"Type": "FormattedText", "Text": p_text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_fourth_level_title(self, p_text, p_pos=None):
        """Method description"""
        text = "{}\n{}\n".format(p_text, self._underline(p_text, "-"))
        text += "\n"
        element = {"Type": "FourthLevelTitle", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_paragraph(self, p_text, p_level=0, p_pos=None):
        """Method description"""
        text = p_text.strip().replace("\n", " ")
        while text.find("  ") >= 0:
            text = text.replace("  ", " ")
        text = "{}{}\n\n".format(self._make_indent(p_level), text)
        element = {"Type": "Paragraph", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_second_level_title(self, p_text, p_pos=None):
        """Method description"""
        text = "{}\n{}\n{}\n".format(
            self._underline(p_text, "-"), p_text, self._underline(p_text, "-")
        )
        text += "\n"
        element = {"Type": "SecondLevelTitle", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_third_level_title(self, p_text, p_pos=None):
        """Method description"""
        text = "{}\n{}\n".format(p_text, self._underline(p_text, "="))
        text += "\n"
        element = {"Type": "ThirdLevelTitle", "Text": text}
        pos = self._insert_at(element, p_pos)
        return pos

    def add_toctree(
        self,
        p_toc_items=None,
        p_maxdepth=None,
        p_caption=None,
        p_numbered=True,
        p_pos=None,
    ):
        if p_toc_items is None:
            p_toc_items = []
        text = ".. toctree::\n"
        if p_maxdepth > 0:
            text += "{}:maxdepth: {}\n".format(self._make_indent(1), p_maxdepth)
        if p_caption:
            text += "{}:caption: {}\n".format(self._make_indent(1), p_caption)
        if p_numbered:
            text += "{}:numbered:\n".format(self._make_indent(1))
        text += "\n"
        for item in p_toc_items:
            text += "{}{}\n".format(self._make_indent(1), item)
        text += "\n"

        element = {"Type": "TocTree", "Text": text, "Items": p_toc_items}
        pos = self._insert_at(element, p_pos)
        return pos
        pass

    def _insert_at(self, p_element, p_pos):
        pos = p_pos
        if pos is None or pos >= self.element_cntr:
            pos = self.element_cntr
            self.elements[pos] = p_element
        else:
            for x in range(self.element_cntr, pos, -1):
                self.elements[x] = self.elements[x - 1].copy()
            self.elements[pos] = p_element
        self.element_cntr += 1
        return pos

    def _make_indent(self, p_level):
        prefix = ""
        for i in range(self.tab_len * p_level):
            prefix += " "
        return prefix

    @staticmethod
    def _underline(p_text, p_template):
        underline = ""
        for i in range(len(p_text)):
            underline += p_template
        return underline

    def write_text(self, p_pth: Path = None):
        self.contents = ""
        if p_pth:
            self.src_pth = p_pth
        for element in sorted(self.elements):
            self.contents += self.elements[element]["Text"]
        self.src_pth.write_text(self.contents)
        pass


class PackageItException(Exception):
    """
    Error handling in PackageIt is done with exceptions. This class is the base of all exceptions raised by PackageIt
    Some other types of exceptions might be raised by underlying libraries.
    """

    def __init__(self, status, data):
        super().__init__()
        self.__code = status[0]
        self.__data = data
        self.__title = status[1]
        print(msg_error(f"{self.__code}:{self.__title}"))
        print(msg_error("\n".join(self.__data)))

    @property
    def code(self):
        """
        The (decoded) data returned by the PackageIt API
        """
        return self.__code

    @property
    def data(self):
        """
        The (decoded) data returned by the PackageIt API
        """
        return self.__data

    @property
    def title(self):
        """
        The status returned by the PackageIt API
        """
        return self.__title

    def __str__(self):
        return f"{self.__code}: {self.__title}"


class OldVersionException(PackageItException):
    """
    Exception raised if the PyPI version is later or equal to the intended GitHub/PackageIt/Release.
    """


class ReadMe(RSTBuilder):
    def __init__(self, p_src_pth):
        super().__init__(p_src_pth)
        self.src_pth = p_src_pth / 'README.rst'
        pass

    def create_body_from_template(self, p_body_pth, p_templ_body_pth):
        if not p_body_pth.exists():
            shutil.copy(p_templ_body_pth, p_body_pth)
        pass


def init_logger():
    logger = logging.getLogger(_PROJ_NAME)
    logger.setLevel(beeutils.DEF_LOG_LEV)
    file_handle = logging.FileHandler(beeutils.LOG_FILE_NAME, mode="w")
    file_handle.setLevel(beeutils.DEF_LOG_LEV_FILE)
    console_handle = logging.StreamHandler()
    console_handle.setLevel(beeutils.DEF_LOG_LEV_CON)
    file_format = logging.Formatter(
        beeutils.LOG_FILE_FORMAT, datefmt=beeutils.LOG_DATE_FORMAT
    )
    console_format = logging.Formatter(beeutils.LOG_CONSOLE_FORMAT)
    file_handle.setFormatter(file_format)
    console_handle.setFormatter(console_format)
    logger.addHandler(file_handle)
    logger.addHandler(console_handle)


def read_args():
    arg_parser = argparse.ArgumentParser(description="Get configuration parameters")
    arg_parser.add_argument(
        "project_name",
        nargs="+",
        help="Project name",
    )
    arg_parser.add_argument(
        "-c",
        "--config-path",
        help="Config file name",
        default=arg_parser.prog[: arg_parser.prog.find(".") + 1] + "ini",
    )
    arg_parser.add_argument(
        "-e", "--arc-extern-dir", help="Path to external archive", default=None
    )
    arg_parser.add_argument(
        "-t",
        "--token-dir",
        help="Directory containing tokens for Pypi, GitHub and ReadTheDocs.",
        default=os.environ["HOMEPATH"],
    )
    args = arg_parser.parse_args()
    # arc_extern_dir: object = args.arc_extern_dir
    ini_path = args.config_path
    # project_name = args.project_name[0]
    # token_dir = Path(args.token_dir)
    return args.project_name[0], ini_path, args.arc_extern_dir, Path(args.token_dir)


_status_codes = {
    # Informational.
    1000: (
        1000,
        "Placeholder",
    ),
    # Version.
    1100: (
        1100,
        "No later version",
    ),
}


if __name__ == "__main__":
    project_name, ini_pth, arc_extern_dir, token_dir = read_args()
    init_logger()
    b_tls = Archiver(
        _PROJ_DESC,
        _PROJ_PATH,
        p_app_ini_file_name=ini_pth,
        p_arc_extern_dir=arc_extern_dir,
    )
    b_tls.print_header(p_cls=False)
    package_it = PackageIt(
        ini_pth, project_name, p_token_dir=token_dir, p_logger_name=False
    )
    if package_it.success:
        package_it.run()
    b_tls.print_footer()
