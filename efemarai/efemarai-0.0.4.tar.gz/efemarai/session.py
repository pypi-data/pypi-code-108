import os
import re
from datetime import datetime
from glob import glob

import boto3
import requests
import validators
import yaml
from appdirs import user_config_dir

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TimeRemainingColumn
from rich.prompt import Confirm, Prompt

from smart_open import smart_open

from efemarai.project import Project


console = Console()


class Session:
    @staticmethod
    def _fetch_token(url, username, password):
        try:
            response = requests.post(
                url + "auth/sdk-token/",
                json={"username": username, "password": password},
            )

            if not response.ok:
                console.print(":poop: Invalid username or password", style="red")
                return None

            return response.json()["token"]

        except requests.exceptions.ConnectionError:
            console.print(":poop: Unreachable URL", style="red")
            return None

    @staticmethod
    def _user_setup(config_file=None):
        console.print(":rocket:  [bold]Welcome to Efemarai![/bold]\n", style="#00a9ff")

        if Session._read_config(config_file) is None:
            console.print("Let's set up things quickly.")
        else:
            if not Confirm.ask(
                "Do you want to overwrite existing config?", default=False
            ):
                return

        console.print("")

        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)

        while True:
            url = Prompt.ask("Platform URL", default=f"https://{username}.efemarai.com")

            if not re.match(r"^https?://", url):
                url = "https://" + url

            if not url.endswith("/"):
                url += "/"

            if validators.url(url):
                break

            console.print("[prompt.invalid]:poop: Invald URL")

        token = Session._fetch_token(url, username, password)

        if token is None:
            return None

        config = {"username": username, "url": url, "token": token}

        if config_file is None:
            config_dir = user_config_dir(appname="efemarai")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, "config.yml")

        console.print(f":gear: Saving config in {config_file}", style="green")

        with open(config_file, "w") as f:
            yaml.dump(config, f)

        return config

    @staticmethod
    def _read_config(config_file=None):
        if config_file is None:
            config_file = os.path.join(
                user_config_dir(appname="efemarai"), "config.yml"
            )

        if not os.path.isfile(config_file):
            return None

        return Session._load_config_file(config_file)

    @staticmethod
    def _save_config_file(data, filename):
        with open(filename, "w") as f:
            yaml.dump(data, f)

    @staticmethod
    def _load_config_file(filename):
        with open(filename) as f:
            contents = f.read()
        return yaml.safe_load(os.path.expandvars(contents))

    @staticmethod
    def _progress_bar():
        return Progress(
            SpinnerColumn(style="green"),
            "[progress.description]{task.description}",
            BarColumn(complete_style="default"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            transient=True,
        )

    def __init__(self, token=None, url=None, config_file=None):
        self.token = token
        self.url = url

        if self.token is None or self.url is None:
            config = self._read_config(config_file)

            if config is None:
                config = self._user_setup(config_file)

            self.token = config["token"]
            self.url = config["url"]

        self._access_requests = {}

    def load(self, filename):
        config = self._load_config_file(filename)

        project = self.project(**config["project"])

        models = [project.model(**model_config) for model_config in config["models"]]

        datasets = [
            project.dataset(**dataset_config) for dataset_config in config["datasets"]
        ]

        domains = []
        for domain_config in config["domains"]:
            if "file" in domain_config:
                domain_config = self._load_config_file(domain_config["file"])["domain"]

            domains.append(project.domain(**domain_config))

        return {
            "project": project,
            "datasets": datasets,
            "domains": domains,
            "models": models,
        }

    @property
    def projects(self):
        return [
            Project(
                self,
                project["id"],
                project["name"],
                project["description"],
                project["problem_type"],
            )
            for project in self._get("api/projects")
        ]

    def project(self, name, description=None, problem_type=None):
        project = next((p for p in self.projects if p.name == name), None)

        if project is None:
            project = Project.create(self, name, description, problem_type)

        return project

    def _get(self, endpoint, json=None, params=None):
        return self._make_request(requests.get, endpoint, json, params)

    def _post(self, endpoint, json=None, params=None):
        return self._make_request(requests.post, endpoint, json, params)

    def _put(self, endpoint, json=None, params=None):
        return self._make_request(requests.put, endpoint, json, params)

    def _delete(self, endpoint, json=None, params=None):
        return self._make_request(requests.delete, endpoint, json, params)

    def _make_request(self, method, endpoint, json=None, params=None):
        url = self.url
        if not url.endswith("/") and not endpoint.startswith("/"):
            url += "/"
        url += endpoint

        response = method(
            url,
            headers={"Authorization": f"Token {self.token}"},
            json=json,
            params=params,
        )

        try:
            return response.json()
        except:
            return None

    def _upload(self, from_url, endpoint):
        if os.path.isdir(from_url):
            self._upload_directory(from_url, endpoint)
        else:
            self._upload_file(from_url, endpoint)

    def _upload_file(self, from_url, endpoint):
        object_key = os.path.basename(from_url)

        with self._progress_bar() as progress:
            task = progress.add_task(
                f"Uploading '{object_key}' ", total=float(os.path.getsize(from_url)),
            )
            callback = lambda num_bytes: progress.advance(task, num_bytes)
            s3, bucket, prefix = self._get_access(endpoint)
            with smart_open(from_url, "rb") as f:
                s3.upload_fileobj(f, bucket, prefix + object_key, Callback=callback)

        console.print(f":heavy_check_mark: Uploaded '{object_key}'", style="green")

    def _upload_directory(self, from_url, endpoint):
        filenames = [
            filename
            for filename in glob(os.path.join(from_url, "**/*"), recursive=True)
            if os.path.isfile(filename)
        ]

        dirname = os.path.basename(os.path.normpath(from_url))

        s3, bucket, prefix = self._get_access(endpoint)

        with self._progress_bar() as progress:
            task = progress.add_task(
                f"Uploading '{dirname}' ", total=float(len(filenames))
            )
            for index, filename in enumerate(filenames):
                object_key = os.path.join(
                    dirname, os.path.relpath(filename, start=from_url)
                )

                with smart_open(filename, "rb") as f:
                    s3.upload_fileobj(f, bucket, prefix + object_key)

                progress.advance(task)

        console.print(f":heavy_check_mark: Uploaded '{dirname}'", style="green")

    def _get_access(self, endpoint):
        access = self._access_requests.get(endpoint, None)

        if access is None or access["Expiration"] <= datetime.now():
            access = self._get(endpoint)
            access["Expiration"] = datetime.strptime(
                access["Expiration"], "%Y-%m-%dT%H:%M:%SZ"
            )
            self._access_requests[endpoint] = access

        s3 = boto3.client(
            "s3",
            aws_access_key_id=access["AccessKeyId"],
            aws_secret_access_key=access["SecretAccessKey"],
            aws_session_token=access["SessionToken"],
            endpoint_url=access["Url"],
        )

        return s3, access["Bucket"], access["Prefix"]
