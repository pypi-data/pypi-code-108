import os
import shutil
import subprocess
import urllib.request

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .models import Packages
from .models import Imports
from .models import Suggests
from .models import Exports
from .models import Arguments
from .models import News
from .models import Tags
from .models import TagMembers
from .urls import CRAN_PKG_CONTRIB_URL


def remove_table(connection_string, table):
    """Remove a table from the database"""
    engine = create_engine(connection_string)
    if table == "packages":
        Packages.__table__.drop(engine)
    if table == "imports":
        Imports.__table__.drop(engine)
    if table == "suggests":
        Suggests.__table__.drop(engine)
    if table == "exports":
        Exports.__table__.drop(engine)
    if table == "arguments":
        Arguments.__table__.drop(engine)
    if table == "news":
        News.__table__.drop(engine)
    if table == "tags":
        Tags.__table__.drop(engine)
    if table == "tag_members":
        TagMembers.__table__.drop(engine)


def tag_packages(connection_string, path_to_r="."):
    """Add the CRAN task view tags to the database and tag the member-packages.
    Tags and TagMembers tables should be emptied before running this.

    :params
    connection_string: connection string for the SQL database
    path_to_r: filepath to the get_task_views.R file
    """
    # Create a configured "Session" class
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    # Create a Session
    session = Session()
    # Get package names and IDs
    result = session.query(Packages.id, Packages.name).all()
    # Create a tags folder
    os.makedirs("./tags")
    # Download task views file
    url = CRAN_PKG_CONTRIB_URL
    views_file = "Views.rds"
    urllib.request.urlretrieve(f"{url}{views_file}", views_file)
    # Use R script to write task views to tags folder
    subprocess.call(["Rscript", "--vanilla", path_to_r + "/get_task_views.R"])
    # Get tags from folder
    tags = os.listdir("./tags")
    for tag in tags:
        name = f"ctv:{tag}"
        # Extract tag topic and member packages
        with open(f"./tags/{tag}") as reader:
            packages = reader.read().split("\n")
        topic = packages.pop(0)
        # Enter tag into database
        tag_info = Tags(name=name, topic=topic)
        session.add(tag_info)
        # Retrieve ID of stored tag
        tag_id = session.query(Tags.id).filter(Tags.name == name).first()[0]
        for package in packages:
            # Find ID matching package name and add to tag members
            package_id = [i[0] for i in result if i[1] == package]
            if len(package_id) > 0:
                package_id = package_id[0]
                tag_member_info = TagMembers(tag_id=tag_id, package_id=package_id)
                session.add(tag_member_info)
    session.commit()
    shutil.rmtree("./tags")
    session.close()
