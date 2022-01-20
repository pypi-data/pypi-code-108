import os
import random
import shutil
import string
import argparse
import requests
from cnvrgv2 import Cnvrg, EndpointKind, EndpointEnvSetup, WebappType, errors
from cnvrgv2.errors import CnvrgHttpError
from cnvrgv2.modules.users import ROLES
from cnvrgv2.modules.users.users_client import UsersClient
from cnvrgv2.modules.workflows.workflow_utils import WorkflowUtils, WorkflowStatuses


def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class LoadCluster:
    LOAD_CLUSTER_FILES_DIR = './.LOAD_CLUSTER_FILES_DIR'
    DEFAULT_NUMBERS = 2000
    DEFAULT_FILES = 1000000  # 1 million
    DEFAULT_USERS = 20
    HELP_DESCRIPTION = """
    This script is used to create a cluster with many workflows, datasets, projects, files etc.
    It is useful for load testing and can be used programmatically too just by importing the script and choosing the list of commands. 
    """

    def __init__(self,
                 domain=None,
                 email=None,
                 password=None,
                 stop=True,
                 num_workflows=DEFAULT_NUMBERS,
                 num_datasets=DEFAULT_NUMBERS,
                 num_projects=DEFAULT_NUMBERS,
                 num_files=DEFAULT_FILES,
                 num_endpoint_charts=DEFAULT_NUMBERS,
                 num_users=DEFAULT_USERS
                 ):
        parser = argparse.ArgumentParser(description=self.HELP_DESCRIPTION)
        parser.add_argument("-d", "--domain", help="choose a domain to run on", type=str, default=domain)
        parser.add_argument("-e", "--email", help="email to login into that domain", type=str, default=email)
        parser.add_argument("-p", "--password", help="password to login into that domain", type=str,
                            default=password)
        parser.add_argument("-nw", "--num-workflows", help="number workflows to create (defaults to 2000)",
                            default=num_workflows, type=int)
        parser.add_argument("-s", "--stop", help="stop workflows after creation (defaults to True)",
                            default=stop, type=bool)
        parser.add_argument("-nd", "--num-datasets", help="number of datasets to create (defaults to 2000)",
                            default=num_datasets, type=int)
        parser.add_argument("-np", "--num-projects", help="number of projects to create (defaults to 2000)",
                            default=num_projects, type=int)
        parser.add_argument("-nf", "--num-files", help="number of files to create into a dataset (defaults to 2000)",
                            default=num_files, type=int)
        parser.add_argument("-nep", "--num-endpoint-charts",
                            help="number of end point chart to create (defaults to 2000)",
                            default=num_endpoint_charts, type=int)
        parser.add_argument("-nu", "--num-users",
                            help="number of users to create for each role (defaults to 20 for each role)",
                            default=num_users, type=int)

        self.args = parser.parse_args()

        self.cnvrg = Cnvrg(domain=self.args.domain, email=self.args.email, password=self.args.password)
        self.proj = self.cnvrg.projects.get('load_proj')
        try:
            # if project doesn't exist it will throw an exception
            self.proj.title
        except CnvrgHttpError:
            self.proj = self.cnvrg.projects.create('load_proj')

        # Create a dir for storing generated files
        if os.path.exists(self.LOAD_CLUSTER_FILES_DIR):
            if os.path.isdir(self.LOAD_CLUSTER_FILES_DIR):
                shutil.rmtree(self.LOAD_CLUSTER_FILES_DIR)
            else:
                os.remove(self.LOAD_CLUSTER_FILES_DIR)

        os.makedirs(self.LOAD_CLUSTER_FILES_DIR)

    def create_cluster(self):
        self._try_to_run("create_many_datasets")
        self._try_to_run("create_many_projects")
        self._try_to_run("create_large_load_dataset")
        self._try_to_run("create_large_project")
        self._try_to_run("create_experiment_with_many_charts")
        self._try_to_run("create_experiment_with_many_artifacts")
        self._try_to_run("create_endpoint_charts")
        self._try_to_run("create_many_users")
        self.destroy()

    def create_many_users(self):
        print("Creating users..")
        random_suffix = random_string(5)
        roles = [ROLES.ADMIN, ROLES.MEMBER, ROLES.MANAGER, ROLES.REVIEWER]

        for role in roles:
            for i in range(self.args.num_users):
                username = str(role) + random_suffix + str(i)
                email = username + "@cnvrg.io"
                password = "qwe123"
                uc = UsersClient(domain=self.args.domain)
                uc.register(username=username, email=email, password=password)
                self.cnvrg.add_user(email, role)
        print("Done creating users.")

    def create_large_project(self):
        print("Creating large project..")
        arguments = {
            "templates": ["small"],
            "command": "python3 -c 1+1"
        }

        for i in range(self.args.num_workflows):
            self._progress_print(i + 1, self.args.num_workflows)
            job = self.proj.workspaces.create(**arguments)
            if self.args.stop:
                job.stop()
            job = self.proj.experiments.create(**{**arguments, "sync_before": False, "sync_after": False})
            if self.args.stop:
                job.stop()
            job = self.proj.endpoints.create(
                title=random_string(10) + str(i),
                templates=["small"],
                kind=EndpointKind.WEB_SERVICE,
                file_name="non-existing.py",
                function_name="predict",
                env_setup=EndpointEnvSetup.PYTHON3
            )
            if self.args.stop:
                job.stop()
            job = self.proj.webapps.create(
                title=random_string(10) + str(i),
                templates=["small"],
                file_name="non-existing.py",
                webapp_type=WebappType.SHINY
            )
            if self.args.stop:
                job.stop()

        print("Done creating large project.")

    def create_many_projects(self):
        print("Creating many projects..")
        for i in range(self.args.num_projects):
            self._progress_print(i + 1, self.args.num_projects)
            self.cnvrg.projects.create("load-project-" + str(i))
        print("Done creating many projects.")

    def create_many_datasets(self):
        print("Creating datasets..")
        for i in range(self.args.num_datasets):
            self._progress_print(i + 1, self.args.num_datasets)
            self.cnvrg.datasets.create("load-datasets-" + str(i))
        print("Done creating datasets.")

    def create_large_load_dataset(self):
        print("Creating large load dataset..")
        dataset = self.cnvrg.datasets.create("large_load_dataset")
        for i in range(self.args.num_files):
            self._progress_print(i + 1, self.args.num_files)
            file_path = "{}/test_file_{}".format(self.LOAD_CLUSTER_FILES_DIR, i)
            tags_file_path = file_path + "_tags.yml"
            with open(file_path, 'w+') as file:
                file.write(file_path)
            with open(tags_file_path, 'w+') as yml:
                yml.write("---\nid: \"{}\"\nsource: \"mega cluster script\"".format(i))

            dataset.put_files([file_path, tags_file_path])
        print("Done creating large load datasets.")

    def create_endpoint_charts(self):
        print("Creating endpoint charts..")
        self.proj.put_files(['examples/load_snippets/endpoint_charts.py'])
        endpoint = self.proj.endpoints.create(
            title=random_string(10),
            templates=["small"],
            kind=EndpointKind.WEB_SERVICE,
            file_name="examples/load_snippets/endpoint_charts.py",
            function_name="predict",
            env_setup=EndpointEnvSetup.PYTHON3
        )

        try:
            WorkflowUtils.wait_for_statuses(endpoint, [WorkflowStatuses.ONGOING])
        except errors.CnvrgFinalStateReached:
            return

        endpoint = self.proj.endpoints.get(endpoint.slug)

        for i in range(2000):
            self._progress_print(i + 1, 2000)
            requests.post(
                endpoint.endpoint_url,
                headers={
                    "Cnvrg-Api-Key": endpoint.api_key,
                },
                data={"doesn't": "even matter"}
            )
        print("Done creating endpoint charts.")

    def create_experiment_with_many_charts(self):
        print("Creating experiment with many charts..")
        self.proj.put_files(['examples/load_snippets/experiment_with_charts.py'])
        self.proj.experiments.create(
            title="all possible charts experiment",
            templates=["small"],
            command="python3 examples/load_snippets/experiment_with_charts.py",
            sync_before=False,
            sync_after=False
        )
        print("Done creating experiment with many charts.")

    def create_experiment_with_many_artifacts(self):
        print("Creating experiment with many artifacts..")
        self.proj.put_files(["examples/load_snippets/experiment_with_many_artifacts.py"])
        self.proj.experiments.create(
            title="a lot of artifacts experiment",
            templates=["small"],
            command="python3 examples/load_snippets/experiment_with_many_artifacts.py",
            sync_before=False,
            sync_after=False
        )
        print("Done creating experiment with many artifacts.")

    def destroy(self):
        shutil.rmtree(self.LOAD_CLUSTER_FILES_DIR)

    def _try_to_run(self, method_name: str):
        try:
            getattr(self, method_name)()

        except Exception as e:
            print("{} has failed, exception: {}".format(method_name, str(e)))

    def _progress_print(self, current, total):
        percentage = current / total
        progress = "<"
        remaining = int(percentage * 10)
        for i in range(remaining):
            progress += "="
        for i in range(10 - remaining):
            progress += "-"
        progress += "> {}/{}".format(current, total)

        print(progress, end="\r")

        # last progress report add new line
        if total == current:
            print()


def createLoadCuster():
    LoadCluster().create_cluster()


if __name__ == "__main__":
    cluster = LoadCluster()
    cluster.create_cluster()
