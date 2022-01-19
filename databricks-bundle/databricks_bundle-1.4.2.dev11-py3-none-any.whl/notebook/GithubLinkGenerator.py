import IPython
import os
import sys
import tomlkit
import traceback

from pathlib import Path
from inspect import getsource


class GithubLinkGenerator:
    def __get_repo_name(self, module):
        special_repos = {
            "daipecore": "daipe-core",
            "featurestorebundle": "feature-store-bundle"
        }

        if module in special_repos.keys():
            return special_repos[module]

        return self.__get_repo_name_with_bundle(module)

    def __get_repo_name_with_bundle(self, module):
        index_of_bundle = module.find("bundle")

        return module[:index_of_bundle] + "-" + module[index_of_bundle:]

    def __get_module_version(self, module_name):
        base_path = Path("/".join(list(Path.cwd().parts[0:5])))
        lockfile_path = base_path.joinpath("poetry.lock")
        assert(module_name == "databricks-bundle")
        with lockfile_path.open("r") as f:
            config = tomlkit.parse(f.read())

        for module in config["package"]:
            if module["name"] == module_name:
                return module["version"]

        raise Exception(
            "Specified module could not be found, make sure the the module is imported and developed by DAIPE")

    def __get_display_html(self):
        ipython = IPython.get_ipython()

        if not hasattr(ipython, "user_ns") or "displayHTML" not in ipython.user_ns:
            raise Exception("displayHTML cannot be resolved")

        return ipython.user_ns["displayHTML"]

    def __get_github_url_from_module(self, module):
        module_path = module.__module__
        module_name_parent = module_path.split(".")[0]
        github_repo_name = self.__get_repo_name(module_name_parent)
        module_file_path = module_path.replace(".", "/") + ".py"
        version = self.__get_module_version(github_repo_name)

        return self.__generate__github_url(github_repo_name, version, module_file_path)

    def __generate__github_url(self, repo_name: str, version: str, file_path: str, lineno: str = ""):
        github_path = "https://github.com/daipe-ai/"

        return f"{github_path}{repo_name}/blob/v{version}/src/{file_path}#L{lineno}"

    def __get_file_path_from_stack_trace(self, stack_trace):
        filename_with_error = stack_trace.filename

        return filename_with_error.split("site-packages")[1]

    def generate_link_from_module(self, module):
        base_module_name = module.__module__.split(".")[-1]
        display_html = self.__get_display_html()
        module_github_url = self.__get_github_url_from_module(module)
        html_method_def = getsource(module).replace(
            "\n", "<br>&nbsp;&nbsp;&nbsp;&nbsp;")
        html_link = f"<a href=\"{module_github_url}\">Github source file for module {base_module_name}</a>"
        html_string = f"{html_method_def}<br>{html_link}"
        
        return display_html(html_string)

    def generate_link_from_traceback(self, tb):
        last_stack_trace = traceback.extract_tb(tb)[-1]
        file_path = self.__get_file_path_from_stack_trace(last_stack_trace)
        module_name = file_path.split("/")[1]
        github_repo_name = self.__get_repo_name_with_bundle(module_name)
        version = self.__get_module_version(github_repo_name)

        return self.__generate__github_url(github_repo_name, version, file_path, str(last_stack_trace.lineno))
