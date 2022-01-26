import datetime

from sqlalchemy import create_engine, or_, and_, desc
from sqlalchemy.orm import sessionmaker

from .models import Packages
from .models import Imports
from .models import Suggests
from .models import Exports
from .models import Arguments
from .models import News
from .models import Tags
from .models import TagMembers


def make_querymaker(connect_string):
    """Instantiates QueryMaker class"""
    engine = create_engine(connect_string, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    query_maker = QueryMaker(Session())
    return query_maker


class NotFoundError(Exception):
    pass


class QueryMaker:
    def __init__(self, session):
        self.session = session

    def get_names(self):
        """Gets unique names of all packages in database

        return: list of package names
        """
        names = self.session.query(Packages.name).distinct()
        names = [element for tupl in names for element in tupl]
        return names

    def check_name_and_version(self, package_names, versions):
        """Checks that package names and corresponding versions are in database.
        Exception is raised if a package or a respective version is not.

        :params
        package_names: list of package names
        versions: list of corresponding package version numbers
        """
        package_filter = or_(
            and_(Packages.name == package_names[i], Packages.version == versions[i])
            for i in range(len(package_names))
        )
        result = (
            self.session.query(Packages.name, Packages.version)
            .filter(package_filter)
            .all()
        )
        for p_id, package in enumerate(package_names):
            version = versions[p_id]
            db_entry = [i for i in result if i == (package, version)]
            if len(db_entry) == 0:
                raise NotFoundError(f"{package} v{version}")

    def get_latest_versions(self, package_names):
        """Get all stored version numbers

        :param package_names: list of package names
        :return: a list of dictionaries with package version numbers
        """
        result = (
            self.session.query(Packages.name, Packages.version)
            .filter(Packages.name.in_(package_names))
            .order_by(Packages.date.desc())
            .all()
        )
        result_list = []
        for package in package_names:
            versions = [i[1] for i in result if i[0] == package]
            if len(versions) == 0:
                raise NotFoundError(package)
            package_dict = {"package": package, "versions": versions}
            result_list.append(package_dict)
        return result_list

    def query_imports(self, package_names, versions):
        """Get package imports

        :params
        package_names: list of package names
        versions: list of corresponding package version numbers

        :return: a list of dictionaries with package imports
        """
        self.check_name_and_version(package_names, versions)
        package_filter = or_(
            and_(Packages.name == package_names[i], Packages.version == versions[i])
            for i in range(len(package_names))
        )
        result = (
            self.session.query(
                Imports.name, Imports.version, Packages.name, Packages.version
            )
            .join(Packages, Packages.id == Imports.package_id)
            .filter(package_filter)
            .all()
        )
        result_list = []
        for p_id, package in enumerate(package_names):
            imports = [
                {"name": i[0], "version": i[1]}
                for i in result
                if i[2:] == (package, versions[p_id])
            ]
            package_dict = {
                "package": package,
                "version": versions[p_id],
                "imports": imports,
            }
            result_list.append(package_dict)
        return result_list

    def query_suggests(self, package_names, versions):
        """Get package suggests

        :params
        package_names: list of package names
        versions: list of corresponding package version numbers

        :return: a list of dictionaries with package suggests
        """
        self.check_name_and_version(package_names, versions)
        package_filter = or_(
            and_(Packages.name == package_names[i], Packages.version == versions[i])
            for i in range(len(package_names))
        )
        result = (
            self.session.query(
                Suggests.name, Suggests.version, Packages.name, Packages.version
            )
            .join(Packages, Packages.id == Suggests.package_id)
            .filter(package_filter)
            .all()
        )
        result_list = []
        for p_id, package in enumerate(package_names):
            suggests = [
                {"name": i[0], "version": i[1]}
                for i in result
                if i[2:] == (package, versions[p_id])
            ]
            package_dict = {
                "package": package,
                "version": versions[p_id],
                "suggests": suggests,
            }
            result_list.append(package_dict)
        return result_list

    def query_exports(self, package_names, versions):
        """Get package exports

        :params
        package_names: list of package names
        versions: list of corresponding package version numbers

        :return: a list of dictionaries with package exports
        """
        self.check_name_and_version(package_names, versions)
        package_filter = or_(
            and_(Packages.name == package_names[i], Packages.version == versions[i])
            for i in range(len(package_names))
        )
        result = (
            self.session.query(
                Exports.name, Exports.type, Packages.name, Packages.version
            )
            .join(Packages, Packages.id == Exports.package_id)
            .filter(package_filter)
            .all()
        )
        result_list = []
        for p_id, package in enumerate(package_names):
            exports = [
                {"name": i[0], "type": i[1]}
                for i in result
                if i[2:] == (package, versions[p_id])
            ]
            package_dict = {
                "package": package,
                "version": versions[p_id],
                "exports": exports,
            }
            result_list.append(package_dict)
        return result_list

    def query_functions(self, package_names, versions):
        """Get names of package functions and their arguments

        :params
        package_names: list of package names
        versions: list of corresponding package version numbers

        :return: a list of dictionaries with package functions, arguments and their
        default values
        """
        self.check_name_and_version(package_names, versions)
        package_filter = or_(
            and_(Packages.name == package_names[i], Packages.version == versions[i])
            for i in range(len(package_names))
        )
        result = (
            self.session.query(
                Packages.name,
                Packages.version,
                Arguments.function,
                Arguments.name,
                Arguments.default,
            )
            .join(Arguments, Arguments.package_id == Packages.id)
            .filter(package_filter)
            .all()
        )
        result_list = []
        for p_id, package in enumerate(package_names):
            functions = set(
                [i[2] for i in result if i[:2] == (package, versions[p_id])]
            )
            function_list = []
            for function in functions:
                arguments = [
                    {"name": i[3], "value": i[4]}
                    for i in result
                    if i[:3] == (package, versions[p_id], function)
                ]
                function_list.append({"name": function, "arguments": arguments})
            package_dict = {
                "package": package,
                "version": versions[p_id],
                "functions": function_list,
            }
            result_list.append(package_dict)
        return result_list

    def get_new_packages(self, since_date=None, tags=None):
        """Get list of new packages filtered by date and tags

        :params
        since_date: datetime object with start-date for search
        tags: list of tag names to filter the search

        :return: a list of dictionaries, one for each new package
        """
        since_date = since_date or datetime.datetime.utcnow() - datetime.timedelta(
            days=30
        )
        package_filters = [Packages.date >= since_date]
        package_filters.append(Packages.release_number == 1)  # initial versions only
        if tags:
            package_filters.append(Tags.name.in_(tags))
            pkgs = (
                self.session.query(
                    Packages.name,
                    Packages.version,
                    Packages.date,
                    Packages.title,
                    Packages.description,
                )
                .join(TagMembers, Packages.id == TagMembers.package_id)
                .join(Tags, Tags.id == TagMembers.tag_id)
                .filter(and_(*package_filters))
                .subquery()
            )
        else:
            pkgs = (
                self.session.query(
                    Packages.name,
                    Packages.version,
                    Packages.date,
                    Packages.title,
                    Packages.description,
                )
                .filter(and_(*package_filters))
                .subquery()
            )
        return [
            {
                "name": res[0],
                "initial_version": res[1],
                "date": res[2],
                "title": res[3],
                "description": res[4],
            }
            for res in self.session.query(
                pkgs.c.name,
                pkgs.c.version,
                pkgs.c.date,
                pkgs.c.title,
                pkgs.c.description,
            ).order_by(desc(pkgs.c.date))
        ]

    def get_package_updates(self, since_date=None, tags=None):
        """Get list of package updates filtered by date and tags

        :params
        since_date: datetime object with start-date for search
        tags: list of tag names to filter the search

        :return: a list of dictionaries, one for each update
        """
        since_date = since_date or datetime.datetime.utcnow() - datetime.timedelta(
            days=30
        )
        package_filters = [Packages.date >= since_date]
        package_filters.append(
            Packages.release_number > 1
        )  # updates to existing packages
        if tags:
            package_filters.append(Tags.name.in_(tags))
            pkgs = (
                self.session.query(Packages.name, Packages.version, Packages.date)
                .join(TagMembers, Packages.id == TagMembers.package_id)
                .join(Tags, Tags.id == TagMembers.tag_id)
                .filter(and_(*package_filters))
                .subquery()
            )
        else:
            pkgs = (
                self.session.query(Packages.name, Packages.version, Packages.date)
                .filter(and_(*package_filters))
                .subquery()
            )
        return [
            {
                "name": res[0],
                "new_version": res[1],
                "date": res[2],
            }
            for res in self.session.query(
                pkgs.c.name, pkgs.c.version, pkgs.c.date
            ).order_by(desc(pkgs.c.date))
        ]

    def get_removed_packages(self, since_date=None):
        """Get list of removed packages filtered by date

        :params
        since_date: datetime object with start-date for search

        :return: a list of dictionaries, one for each removed package
        """
        since_date = since_date or datetime.datetime.utcnow() - datetime.timedelta(
            days=30
        )
        # Database was populated on 12th July 2020: since_date must be after
        earliest_date = datetime.datetime(year=2020, month=7, day=13)
        if earliest_date > since_date:
            since_date = earliest_date
        pkgs = (
            self.session.query(
                Packages.name, Packages.last_modified, Packages.package_type
            )
            .filter(Packages.last_modified >= since_date)
            .order_by(desc(Packages.last_modified))
            .all()
        )
        removed = []
        unique_names = set([p[0] for p in pkgs])
        for package in unique_names:
            matching = [i for i in pkgs if i[0] == package]
            # Check if most recent version is archived
            if matching[0][2] == "archived":
                removed.append(matching[0][:2])
        # Sort output list by date (latest first)
        removed.sort(key=lambda x: x[1], reverse=True)
        return [{"name": res[0], "date": res[1]} for res in removed]

    def get_news_by_tag(self, since_date=None, tags=None):
        """Get list of news items filtered by date and tags

        :params
        since_date: datetime object with start-date for news search
        tags: list of tag names to filter the search

        :return: a list of dictionaries, one for each news category
        """
        since_date = since_date or datetime.datetime.utcnow() - datetime.timedelta(
            days=30
        )
        package_filters = tags and [Tags.name.in_(tags)] or []
        package_filters.append(Packages.date >= since_date)
        pkgs = (
            self.session.query(
                Packages.id, Packages.name, Packages.version, Packages.date
            )
            .join(TagMembers, Packages.id == TagMembers.package_id)
            .join(Tags, Tags.id == TagMembers.tag_id)
            .filter(and_(*package_filters))
            .subquery()
        )
        return [
            {
                "name": res[0],
                "version": res[1],
                "date": res[2],
                "type": "updated package",
                "news_category": res[4],
                "news_text": res[3],
            }
            for res in self.session.query(
                pkgs.c.name, pkgs.c.version, pkgs.c.date, News.text, News.category
            )
            .join(News, pkgs.c.id == News.package_id)
            .order_by(desc(pkgs.c.date))
        ]

    def get_news_by_package(self, since_date=None, packages=None):
        """Get list of news items filtered by date and packages

        :params
        since_date: datetime object with start-date for news search
        packages: list of names of CRAN packages to filter the search

        :return: a list of dictionaries, one for each news category
        """
        since_date = since_date or datetime.datetime.utcnow() - datetime.timedelta(
            days=30
        )
        package_filters = packages and [Packages.name.in_(packages)] or []
        package_filters.append(Packages.date >= since_date)
        pkgs = (
            self.session.query(
                Packages.id, Packages.name, Packages.version, Packages.date
            )
            .filter(and_(*package_filters))
            .subquery()
        )
        return [
            {
                "name": res[0],
                "version": res[1],
                "date": res[2],
                "type": "updated package",
                "news_category": res[4],
                "news_text": res[3],
            }
            for res in self.session.query(
                pkgs.c.name, pkgs.c.version, pkgs.c.date, News.text, News.category
            )
            .join(News, pkgs.c.id == News.package_id)
            .order_by(desc(pkgs.c.date))
        ]

    def get_news_by_version(self, package_names, versions):
        """Get list of news items filtered by package version

        :params
        package_names: list of names of CRAN packages
        versions: list of versions, one for each package

        :return: a list of news dictionaries, ordered by the input
        """
        package_filter = or_(
            and_(Packages.name == package_names[i], Packages.version == versions[i])
            for i in range(len(package_names))
        )
        result = (
            self.session.query(
                Packages.name, Packages.version, News.text, News.category
            )
            .filter(package_filter)
            .join(News, Packages.id == News.package_id)
            .all()
        )
        result_list = []
        for p_id, package in enumerate(package_names):
            # Get news for each version (empty list if no news)
            news = [
                {"category": i[3], "text": i[2]}
                for i in result
                if i[0] == package and i[1] == versions[p_id]
            ]
            news_dict = {"name": package, "version": versions[p_id], "news": news}
            result_list.append(news_dict)
        return result_list

    def get_tags(self):
        """Get list of all tag names, including topic"""
        tags = self.session.query(Tags.name, Tags.topic).distinct()
        tags = [{"name": i[0], "topic": i[1]} for i in tags]
        return tags

    def query_tag_members(self, tags):
        """Get packages belonging to a list of tags

        :param tags: list of tags

        :return: a list of dictionaries with tag member-packages
        """
        result = (
            self.session.query(Packages.name, Tags.name)
            .join(TagMembers, Packages.id == TagMembers.package_id)
            .join(Tags, Tags.id == TagMembers.tag_id)
            .filter(Tags.name.in_(tags))
            .all()
        )
        result_list = []
        for tag in tags:
            members = [i[0] for i in result if i[1] == tag]
            if len(members) == 0:
                if len([i for i in result if i[1] == tag]) == 0:
                    # Tag is not in database
                    raise NotFoundError(tag)
            result_list.append({"tag": tag, "packages": members})
        return result_list

    def query_package_tags(self, package_names):
        """Get package tags

        :param package_names: list of package names

        :return: a list of dictionaries with package tags
        """
        result = (
            self.session.query(Tags.name, Tags.topic, Packages.name)
            .join(TagMembers, Tags.id == TagMembers.tag_id)
            .join(Packages, Packages.id == TagMembers.package_id)
            .filter(Packages.name.in_(package_names))
            .all()
        )
        result_list = []
        for package in package_names:
            tags = [{"name": i[0], "topic": i[1]} for i in result if i[2] == package]
            if len(tags) == 0:
                if len([i for i in result if i[2] == package]) == 0:
                    # Package is not in database
                    raise NotFoundError(package)
            result_list.append({"package": package, "tags": tags})
        return result_list


def get_diff(result_list):
    """Get import or suggest diffs using input list of dictionaries

    :params
    result_list: output from query_imports() or query_suggests()

    :return: a list of dictionaries with added, removed and changed (version numbers)
    packages
    """
    diff_list = []
    if "imports" in result_list[0]:
        key = "imports"
    else:
        key = "suggests"
    num_pairs = int(len(result_list) / 2)
    for pair_id in range(num_pairs):
        v1res = result_list[pair_id * 2]
        v2res = result_list[(pair_id * 2) + 1]
        set1 = set([(i["name"], i["version"]) for i in v1res[key]])
        set2 = set([(i["name"], i["version"]) for i in v2res[key]])
        diff1 = set1 - set2
        diff2 = set2 - set1
        # Check for version changes
        changed = []
        added = []
        removed = []
        for i in diff1:
            was_changed = False
            for j in diff2:
                if i[0] == j[0]:
                    changed.append({"package": i[0], "old": j[1], "new": i[1]})
                    was_changed = True
                    break
            if not was_changed:
                added.append({"package": i[0], "version": i[1]})
        for i in diff2:
            was_changed = False
            for j in diff1:
                if i[0] == j[0]:
                    was_changed = True
                    break
            if not was_changed:
                removed.append({"package": i[0], "version": i[1]})
        pair_diff = {
            "name": v1res["package"],
            "new": v1res["version"],
            "old": v2res["version"],
            "added": added,
            "removed": removed,
            "version_changes": changed,
        }
        diff_list.append(pair_diff)
    return diff_list


def get_export_diff(result_list):
    """Get export diffs using input list of dictionaries

    :params
    result_list: output from query_exports()

    :return: a list of dictionaries with added and removed exports
    """
    diff_list = []
    num_pairs = int(len(result_list) / 2)
    for pair_id in range(num_pairs):
        v1res = result_list[pair_id * 2]
        v2res = result_list[(pair_id * 2) + 1]
        set1 = set([(i["name"], i["type"]) for i in v1res["exports"]])
        set2 = set([(i["name"], i["type"]) for i in v2res["exports"]])
        diff1 = set1 - set2
        diff2 = set2 - set1
        # Check which exports have been added / removed
        added = []
        removed = []
        for i in diff1:
            added.append({"name": i[0], "type": i[1]})
        for i in diff2:
            removed.append({"name": i[0], "type": i[1]})
        pair_diff = {
            "name": v1res["package"],
            "new": v1res["version"],
            "old": v2res["version"],
            "added": added,
            "removed": removed,
        }
        diff_list.append(pair_diff)
    return diff_list


def get_function_diff(result_list):
    """Get function diffs using input list of dictionaries

    :params
    result_list: output from query_functions()

    :return: a list of dictionaries with added and removed functions and argument
    changes for retained functions
    """
    diff_list = []
    num_pairs = int(len(result_list) / 2)
    for pair_id in range(num_pairs):
        v1res = result_list[pair_id * 2]
        v2res = result_list[(pair_id * 2) + 1]
        # Get functions of the two versions using dict keys
        new = set([i["name"] for i in v1res["functions"]])
        old = set([i["name"] for i in v2res["functions"]])
        # Check which functions have been added / removed
        added = new - old
        removed = old - new
        # Check argument difference for functions retained in latest version
        retained = new - added
        changed = []
        added_args = []
        removed_args = []
        for f in retained:
            arguments1 = [i["arguments"] for i in v1res["functions"] if i["name"] == f][
                0
            ]
            arguments2 = [i["arguments"] for i in v2res["functions"] if i["name"] == f][
                0
            ]
            set1 = set([(i["name"], i["value"]) for i in arguments1])
            set2 = set([(i["name"], i["value"]) for i in arguments2])
            diff1 = set1 - set2
            diff2 = set2 - set1
            # Check for added / removed arguments and changed default values
            for i in diff1:
                was_changed = False
                for j in diff2:
                    if i[0] == j[0]:
                        changed.append(
                            {"function": f, "argument": i[0], "old": j[1], "new": i[1]}
                        )
                        was_changed = True
                        break
                if not was_changed:
                    added_args.append({"function": f, "argument": i[0]})
            for i in diff2:
                was_changed = False
                for j in diff1:
                    if i[0] == j[0]:
                        was_changed = True
                        break
                if not was_changed:
                    removed_args.append({"function": f, "argument": i[0]})
        pair_diff = {
            "name": v1res["package"],
            "new": v1res["version"],
            "old": v2res["version"],
            "added_functions": list(added),
            "removed_functions": list(removed),
            "added_arguments": added_args,
            "removed_arguments": removed_args,
            "argument_value_changes": changed,
        }
        diff_list.append(pair_diff)
    return diff_list
