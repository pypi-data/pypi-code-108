import datetime
import glob
import json
import os

import dateutil.parser
import ocdskit.combine  # type: ignore
import ocdskit.util  # type: ignore
import requests
from jinja2 import Environment, PackageLoader, select_autoescape

from ocdsadditions.constants import LATEST_OCDS_SCHEMA_VERSION


def init_repository(directory: str):

    if not os.path.isdir(directory):
        os.makedirs(directory)

    ocids_directory = os.path.join(directory, "contracting_processes")
    if not os.path.isdir(ocids_directory):
        os.makedirs(ocids_directory)

    data: dict = {}

    with open(os.path.join(directory, "ocdsadditions.json"), "w") as fp:
        json.dump(data, fp, indent=4)


class Repository:
    def __init__(self, directory_name: str):
        self.directory_name = directory_name
        if not os.path.isdir(directory_name):
            raise Exception("Directory does not exist")
        if not os.path.isfile(os.path.join(directory_name, "ocdsadditions.json")):
            raise Exception("Additions file not found")

    def add_ocid(self, ocid):

        # TODO: Can we assume OCIDS are always valid directory names?
        ocid_directory = os.path.join(
            self.directory_name, "contracting_processes", ocid
        )
        if not os.path.isdir(ocid_directory):
            os.makedirs(ocid_directory)

        data: dict = {"ocid": ocid}

        with open(
            os.path.join(ocid_directory, "ocdsadditions_contracting_process.json"), "w"
        ) as fp:
            json.dump(data, fp, indent=4)

    def get_contracting_process(self, ocid: str):
        return ContractingProcess(self, ocid)

    def add_external_release_package(self, url: str):
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Non 200 response")

        package_data = r.json()
        if not ocdskit.util.is_release_package(package_data):
            raise Exception("Not a release package")

        releases = package_data["releases"]
        del package_data["releases"]
        for release in releases:
            if not ocdskit.util.is_release(release):
                raise Exception("Not a release")
            contracting_process = self.get_contracting_process(release["ocid"])
            contracting_process.add_release(package_data, release, url)

    def list_ocids(self) -> list:
        out: list = []
        for path in glob.glob(
            os.path.join(
                self.directory_name,
                "contracting_processes",
                "*",
                "ocdsadditions_contracting_process.json",
            )
        ):
            with open(path) as fp:
                data = json.load(fp)
                out.append(data["ocid"])
        return out

    def build_site(self, output_directory: str):
        os.makedirs(output_directory, exist_ok=True)
        ocids: list = self.list_ocids()

        jinja_env = Environment(
            loader=PackageLoader("ocdsadditions"), autoescape=select_autoescape()
        )

        # Root files
        data = {
            "ocids": ocids,
        }
        with open(os.path.join(output_directory, "api.json"), "w") as fp:
            json.dump(data, fp, indent=4)
        with open(os.path.join(output_directory, "index.html"), "w") as fp:
            fp.write(
                jinja_env.get_template("index.html").render(
                    repository=self, ocids=ocids
                )
            )

        # Contracting Processes
        for ocid in ocids:
            contracting_process = self.get_contracting_process(ocid)
            releases = contracting_process.list_releases()
            ocid_directory = os.path.join(output_directory, "contracting_process", ocid)
            os.makedirs(ocid_directory, exist_ok=True)
            data = {
                "ocid": ocid,
                "releases": [r.directory_name for r in releases],
            }
            with open(os.path.join(ocid_directory, "api.json"), "w") as fp:
                json.dump(data, fp, indent=4)

            with open(os.path.join(ocid_directory, "index.html"), "w") as fp:
                fp.write(
                    jinja_env.get_template("contracting_process/index.html").render(
                        repository=self, ocid=ocid, releases=releases
                    )
                )

            # Individual Releases
            for release in releases:
                release_directory = os.path.join(
                    ocid_directory, "release", release.directory_name
                )
                os.makedirs(release_directory, exist_ok=True)
                data = {}
                with open(os.path.join(release_directory, "api.json"), "w") as fp:
                    json.dump(data, fp, indent=4)
                release.write_release_package(
                    os.path.join(release_directory, "release_package.json")
                )

            # A record
            generator = ocdskit.combine.merge(
                [r.get_release_package() for r in releases],
                return_package=True,
            )
            data = next(generator)
            with open(os.path.join(ocid_directory, "record.json"), "w") as fp:
                json.dump(data, fp, indent=4)


class ContractingProcess:
    def __init__(self, repository: Repository, ocid: str):
        self.repository = repository
        self.ocid = ocid

        self.ocid_directory = os.path.join(
            repository.directory_name, "contracting_processes", ocid
        )
        if not os.path.isdir(self.ocid_directory):
            raise Exception("OCID does not exist")
        if not os.path.isfile(
            os.path.join(self.ocid_directory, "ocdsadditions_contracting_process.json")
        ):
            raise Exception("OCID file not found")

    def add_release(self, package_data: dict, release: dict, source_url: str):
        datetime_object = dateutil.parser.parse(release["date"])
        # TODO: Can we assume IDS are always valid directory names?
        dir_name = datetime_object.strftime("%Y-%m-%d-%H-%M-%S") + "-" + release["id"]
        directory = os.path.join(self.ocid_directory, "releases", dir_name)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        data: dict = {
            "url": source_url,
            "id": release["id"],
            "date": datetime_object.isoformat(),
        }

        with open(os.path.join(directory, "ocdsadditions_release.json"), "w") as fp:
            json.dump(data, fp, indent=4)

        with open(os.path.join(directory, "package.json"), "w") as fp:
            json.dump(package_data, fp, indent=4)

        with open(os.path.join(directory, "release.json"), "w") as fp:
            json.dump(release, fp, indent=4)

    def add_empty_release(self, release_id: str):
        if self.does_release_id_exist(release_id):
            raise Exception("Release ID Already exists")
        datetime_object = datetime.datetime.now(datetime.timezone.utc)
        # TODO: Can we assume IDS are always valid directory names?
        dir_name = datetime_object.strftime("%Y-%m-%d-%H-%M-%S") + "-" + release_id
        directory = os.path.join(self.ocid_directory, "releases", dir_name)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        data: dict = {
            "id": release_id,
            "date": datetime_object.isoformat(),
        }

        # TODO add extensions info from existing releases
        # TODO add publisher info from this repo
        # TODO add uri
        package_data: dict = {
            "version": LATEST_OCDS_SCHEMA_VERSION,
            "publishedDate": datetime_object.isoformat(),
            "publisher": {
                "name": "",
                "scheme": "",
                "uid": "",
                "uri": "",
            },
        }

        release_data: dict = {
            "ocid": self.ocid,
            "id": release_id,
            "date": datetime_object.isoformat(),
        }

        with open(os.path.join(directory, "ocdsadditions_release.json"), "w") as fp:
            json.dump(data, fp, indent=4)

        with open(os.path.join(directory, "package.json"), "w") as fp:
            json.dump(package_data, fp, indent=4)

        with open(os.path.join(directory, "release.json"), "w") as fp:
            json.dump(release_data, fp, indent=4)

    def list_releases(self) -> list:
        out: list = []
        for path in glob.glob(
            os.path.join(
                self.ocid_directory, "releases", "*", "ocdsadditions_release.json"
            )
        ):
            out.append(Release(self, path.split("/")[-2]))
        return out

    def does_release_id_exist(self, release_id) -> bool:
        for path in glob.glob(
            os.path.join(
                self.ocid_directory, "releases", "*", "ocdsadditions_release.json"
            )
        ):
            with (open(path)) as fp:
                data = json.load(fp)
                if data["id"] == release_id:
                    return True
        return False


class Release:
    def __init__(self, contracting_process: ContractingProcess, directory_name: str):
        self.contracting_process = contracting_process
        self.directory_name = directory_name

        self.release_directory = os.path.join(
            contracting_process.ocid_directory, "releases", directory_name
        )
        if not os.path.isdir(self.release_directory):
            raise Exception("Release does not exist")
        if not os.path.isfile(
            os.path.join(self.release_directory, "ocdsadditions_release.json")
        ):
            raise Exception("Release file not found")

    def get_release_package(self) -> dict:
        with (
            open(os.path.join(self.release_directory, "ocdsadditions_release.json"))
        ) as fp:
            meta = json.load(fp)
        with (open(os.path.join(self.release_directory, "package.json"))) as fp:
            data = json.load(fp)
        with (open(os.path.join(self.release_directory, "release.json"))) as fp:
            data["releases"] = [json.load(fp)]
        if meta.get("url"):
            # This indicates the releases was "stolen" from elswehere. We should add a "rel" link.
            # These links will become standard in OCDS 1.2, we have been told.
            if not "links" in data["releases"][0]:
                data["releases"][0]["links"] = []
            if not isinstance(data["releases"][0]["links"], list):
                raise Exception("Releases Links section is not a list")
            data["releases"][0]["links"].append(
                {"rel": "canonical", "href": meta["url"]}
            )
        return data

    def write_release_package(self, filename):
        with open(filename, "w") as fp:
            json.dump(self.get_release_package(), fp, indent=4)
