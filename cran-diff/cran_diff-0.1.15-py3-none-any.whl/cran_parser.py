# flake8: noqa

import concurrent.futures
import csv
import os
import pathlib
import shutil
import json

from datetime import datetime

import pandas as pd
import requests
import sqlalchemy

from sqlalchemy.orm import sessionmaker
from requests_file import FileAdapter
from tqdm import tqdm

from .cran_parsing_functions import parse_metadata
from .cran_archive import get_archive_name_versions
from .pkg_parsing_functions import (
    download_package_tar,
    process_package_tar,
)
from .rcom import RCom
from .urls import CRAN_PKG_LIST_URL


class CranParser:
    def __init__(
        self,
        JSON_path,
        package_list_url=CRAN_PKG_LIST_URL,
        download_path="./downloads",
        max_pool=32,
        keep_tar_files=False,
    ):

        # ensure download path exists
        self.set_download_path(download_path)
        self.JSON_path = JSON_path
        self.keep_tar_files = keep_tar_files

        # get list of current packages
        self.set_cran_metadata(package_list_url)

        # create a worker pool for background tasks
        self.set_max_pool(max_pool)

        self.change_current = []
        self.change_archive = []

    def get_r_communicator(self):
        """
        Gets an `RCom` object, to allow communication with R
        """
        try:
            return self.communicator
        except AttributeError:
            self.set_r_communicator()
            return self.communicator

    def set_r_communicator(self):
        """
        Adds an object that allows communication with R
        """
        print("Creating R communication object")
        self.communicator = RCom()

    def set_max_pool(self, max_pool):
        print("Setting max workers in pool to ", max_pool)
        self.MAX_POOL = max_pool

    def search_archive(self):
        """Searches the CRAN archive for recent (<2yr) versions of 
        current packages
        """
        packages = map(lambda x: x[0], self.meta_data)

        def inner(package):
            archive_versions = get_archive_name_versions(package)
            # print("Found archive for ", package)
            return archive_versions

        futures = []
        res = []
        num_archived = []  # number of archived versions
        with concurrent.futures.ThreadPoolExecutor(self.MAX_POOL) as executor:
            for package in packages:
                future = executor.submit(inner, package)
                futures.append(future)
            # once they have all finished
            for f in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                temp = f.result()
                res += temp[0]
                num_archived.append(temp[1])
        self.archive = res
        # Add release number to meta-data using num_archived
#        for p_id, p in enumerate(self.meta_data):
#            release_number = [i[1] for i in num_archived if i[0] == p[0]][0] + 1
#            self.meta_data[p_id] = (p[0], p[1], release_number)

    def initial_db_fill(self):
        """Populates empty JSON data with all CRAN packages, including
        archived versions from the last two years
        """
        print("Search archive")
        self.search_archive()
        self.get_current_packages()
        self.detect_meta_not_stored()
        self.detect_archive_not_stored()
        package_list = self.combine_change()
        initial_length = len(package_list)
        # populate packages incrementally, 100 at a time
        while len(package_list) > 0:
            print(f"Only {len(package_list)}/{initial_length} remaining")
            if len(package_list) > 100:
                self.download_and_parse_packages(package_list[:100])
                package_list = package_list[100:]
            else:
                self.download_and_parse_packages(package_list)
                package_list = []

            self.soft_insert(self.to_insert)

    def update_db(self):
        """Updates JSON data, adding new packages and versions that
        are not currently stored
        """
        print("Get current packages")
        self.get_current_packages()
        print("Detect changes")
        self.detect_meta_not_stored()
        package_list = self.combine_change()
        self.download_and_parse_packages(package_list)
#        self.soft_update()
        self.soft_insert(self.to_insert)

    def combine_change(self):
        """Creates a combined list of current and archived CRAN packages
        that are not currently stored

        :returns: list of packages, including name and version number
        """
        return list(
            map(lambda x: (x[0], x[1], "current"), self.change_current)
        ) + list(map(lambda x: (x[0], x[1], "archived"), self.change_archive))

    def download_and_parse_packages(self, package_list):
        """Downloads and parses CRAN packages

        :params: package_list: list of packages to be parsed

        :creates: self.to_insert: list of dictionaries with imports, 
        suggests, exports, functions, and news for each package
        """
        def inner(package, version, package_type):
            try:
                if package_type == "current":
                    tar_file = download_package_tar(
                        package, version, False, pathlib.Path(self.download_path)
                    )
                elif package_type == "archived":
                    tar_file = download_package_tar(
                        package, version, True, pathlib.Path(self.download_path)
                    )
                if tar_file:
                    return (
                        package,
                        version,
                        package_type,
                        process_package_tar(
                            tar_file, keep_tar_file=self.keep_tar_files
                        ),
                    )
            except Exception as e:
                print(e)

        futures = []
        self.to_insert = []
        with concurrent.futures.ThreadPoolExecutor(self.MAX_POOL) as executor:
            print("Start download and processing")
            # submit those in current list
            for package, version, package_type in package_list:
                future = executor.submit(
                    inner,
                    package=package,
                    version=version,
                    package_type=package_type,
                )
                futures.append(future)
            # as they complete, read news and enter into database
            for future in tqdm(
                concurrent.futures.as_completed(futures), total=len(futures)
            ):
                res = future.result()
                if res:
                    package, version, package_type, data = res
                    lib_loc = os.path.dirname(data["package_location"])
                    export_list = self.read_exports(package, version, lib_loc)
                    news_list = self.read_news(package, version, lib_loc)
                    data.update(
                        {
                            "exports": export_list,
                            "news": news_list,
                            "package": package,
                            "version": version,
                            "package_type": package_type,
                        }
                    )
                    self.to_insert += [data]
                    shutil.rmtree(lib_loc)  # remove package folder

    def soft_update(self):
        package_keys = ["name", "version"]
        downloaded = [(d["name"], d["version"]) for d in self.to_insert]
        new_packages_ix = self.find_new_packages(downloaded)
        print("Adding new packages")
        self.soft_insert([self.to_insert[i] for i in new_packages_ix])
        print("Updating updated packages")
        updated_packages, updated_packages_ix = self.find_updated_packages(downloaded)
        updated_ids = self.find_updated_ids(updated_packages)
        self.set_to_archive(updated_ids)
        print("Adding updated packages to DB")
        self.soft_insert([self.to_insert[i] for i in updated_packages_ix])
        print("Archiving removed packages")
        removed_packages = self.find_removed_package_ids()
        self.set_to_archive(removed_packages)

    def set_to_archive(self, ids):
        print("Archiving packages with ids ", ids)
        updater = (
            sqlalchemy.update(Packages)
            .where(Packages.id.in_(ids))
            .values(package_type="archived", last_modified=datetime.utcnow())
        )
        self.session.execute(updater)

    def find_updated_ids(self, updated_packages):
        names = [x for x, y in updated_packages]
        sub_packages = self.current_packages.query(
            "package_type == 'current' & name == @names"
        )
        ids = list(sub_packages["id"])
        return ids

    def find_new_packages(self, downloaded):
        existing = set(self.current_packages["name"])
        res = [i for i, x in enumerate(downloaded) if x[0] not in existing]
        print("Found ", len(res), " new packages")
        return res

    def find_updated_packages(self, downloaded):
        existing = set(self.current_packages["name"])
        res_ix = [i for i, x in enumerate(downloaded) if x[0] in existing]
        res = [downloaded[i] for i in res_ix]
        print("Found ", len(res), " updated packages")
        return res, res_ix

    def find_removed_package_ids(self):
        sub_packages = self.current_packages.query("package_type == 'current'")
        res = list(set(sub_packages["name"]) - set([x[0] for x in self.meta_data]))
        res = list(sub_packages.query("name == @res")["id"])
        print("Found ", len(res), " removed packages.")
        return res

    def soft_insert(self, data_vals):
        """Store package data in JSON files

        :params: data_vals: list of dictionaries with parsed package
        data, including imports, suggests, exports, functions, and news
        """
        names = []
        versions = []
        for data in data_vals:
            package = data['name']
            version = data['version']
            names.append(package)
            versions.append(version)
            version_path = self.JSON_path + '/' + package + '/' + version
            # Ensure output path exists
            if not os.path.exists(version_path):
                os.makedirs(version_path)
            # Store imports, suggests, exports and news
            with open(version_path + "/imports.json", 'w+') as f:
                f.write(json.dumps(data['imports']))
            with open(version_path + "/suggests.json", 'w+') as f:
                f.write(json.dumps(data['suggests']))
            with open(version_path + "/exports.json", 'w+') as f:
                f.write(json.dumps(data['exports']))
            with open(version_path + "/functions.json", 'w+') as f:
                f.write(json.dumps(data['functions']))
            with open(version_path + "/news.json", 'w+') as f:
                f.write(json.dumps(data['news']))

        # Update version list for each package
        unique = list(set(names))   # remove duplicate names
        for pkg in unique:
            pkg_versions = [v for (i,v) in enumerate(versions) if names[i] == pkg]
            versions_json = self.JSON_path + '/' + pkg + '/versions.json'
            if os.path.exists(versions_json):
                with open(versions_json, 'r') as f:
                    current = json.load(f)
                pkg_versions.extend(current)
            with open(versions_json, 'w+') as f:
                f.write(json.dumps(sorted(pkg_versions, reverse = True)))

        # Update package list
        packages_json = self.JSON_path + '/packages.json'
        if os.path.exists(packages_json):
            with open(packages_json, 'r') as f:
                current = json.load(f)
            names.extend(current)
        names = list(set(names))   # remove duplicate names
        with open(packages_json, 'w+') as f:
            f.write(json.dumps(sorted(names)))

    def read_news(self, package, version, lib_loc):
        """Parses news file

        :params:
        package: package name
        version: version number
        lib_loc: location of package folder

        :returns: a list of dictionaries with news category and text
        """
        communicator = self.get_r_communicator()

        news_file = communicator.write_news(package, version, lib_loc)
        news_list = []
        if os.path.exists(news_file):
            with open(news_file, newline="") as File:
                reader = csv.reader(File)
                for row in reader:
                    if row[0] == version:
                        if row[2] == "NA":
                            category = ""
                        else:
                            category = row[2]
                        text = row[3]
                        news_dict = {"category": category, "text": text}
                        news_list.append(news_dict)
            os.remove(news_file)
        return news_list

    def read_exports(self, package, version, lib_loc):
        """Parses NAMESPACE file

        :params:
        package: package name
        version: version number
        lib_loc: location of package folder

        :returns: a list of dictionaries with export name and type
        """
        communicator = self.get_r_communicator()

        exports_file = communicator.write_exports(package, version, lib_loc)
        export_list = []
        if os.path.exists(exports_file):
            with open(exports_file, newline="") as File:
                reader = csv.reader(File)
                next(reader, None)  # Skip the headers
                for row in reader:
                    export_dict = {"name": row[0], "type": row[1]}
                    export_list.append(export_dict)
            os.remove(exports_file)
        return export_list

    def detect_meta_not_stored(self):
        """Identifies CRAN meta-data that is not currently stored
        """
        cur = list(zip(self.current_packages["name"], self.current_packages["version"]))
        self.change_current = list(filter(lambda x: not x[:2] in cur, self.meta_data))

    def get_change_release_numbers(self):
        stored = list(
            zip(self.current_packages["name"], self.current_packages["release_number"])
        )
        for p_id, p in enumerate(self.change_current):
            stored_numbers = [i[1] for i in stored if i[0] == p[0]]
            if len(stored_numbers) == 0:
                release_number = 1
            else:
                release_number = max(stored_numbers) + 1
            self.change_current[p_id] = (p[0], p[1], release_number)

    def detect_archive_not_stored(self):
        """Identifies CRAN archive versions that are not currently stored
        """
        try:
            cur = list(
                zip(self.current_packages["name"], self.current_packages["version"])
            )
            self.change_archive = list(filter(lambda x: not x[:2] in cur, self.archive))
        except NameError as e:
            raise Exception(
                "You must search the archive before determining what is missing"
            )

    def get_current_packages(self):
        """Searches the JSON data for all stored packages

        :returns: a dictionary with all stored packages and version numbers
        """
        package_list = []
        version_list = []
        if os.path.exists(self.JSON_path + '/packages.json'):
            with open(self.JSON_path + '/packages.json', 'r') as f:
                packages = json.load(f)
            for pkg in packages:
                with open(self.JSON_path + '/' + pkg + '/versions.json', 'r') as f:
                    versions = json.load(f)
                package_list.extend([pkg for i in range(len(versions))])
                version_list.extend(versions)

        self.current_packages = {
            "name": package_list,
            "version": version_list,
        }
        return self.current_packages

    def set_download_path(self, download_path):
        # set somewhere for download
        print("Preparing for downloads in ", download_path)
        self.ensure_download_path(download_path)
        self.download_path = download_path

    def set_cran_metadata(self, url):
        """Obtain CRAN metadata

        :params:
        url: A URL (or local file-path "file://...") defining which packages are to be
        included here
        """
        print("Obtaining CRAN metadata from ", url)
        requests_session = requests.Session()
        requests_session.mount("file://", FileAdapter())

        response = requests_session.get(url)
        output = response.text
        self.meta_data = parse_metadata(output)

    def ensure_download_path(self, download_path):
        """Ensure that the provided download path exists

        :params:
        download_path: A place to store downloaded tars
        """
        os.makedirs(download_path, exist_ok=True)
