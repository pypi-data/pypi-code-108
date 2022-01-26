import click
from making_with_code_cli.mwc_api import MakingWithCodeAPI as API
import yaml

@click.group()
def cli():
    pass

@cli.command()
@click.option("--username", default="localhost", help="Username")
@click.option("--email", default="localhost", help="Email")
@click.option("--host", default="localhost", help="MWC Courseware server.")
def config(username, email, host="localhost"):
    """Configure mwc cli"""
    click.echo("TODO")

@cli.group()
def course():
    "Interact with courses"

@course.command(name="list")
def list_courses():
    "List courses"
    api = API()
    courses = api.get("api/courses")
    print(yaml.dump(courses))

@cli.group()
def assignment():
    "Interact with assignments"

@assignment.command(name="list")
@click.option("--course", help="Filter by course")
def list_assignments(course):
    pass

@cli.group()
def project():
    "Interact with projects"

@project.command(name="list")
def list_projects():
    "List all projects."
    # TODO add an option to specify which assignment
    api = API()
    projects = api.get("api/projects")
    print(yaml.dump(projects))

@cli.group()
def repo():
    "Interact with student repos"

@repo.command(name="list")
@click.option("--user", help="Filter by username")
@click.option("--project", help="Filter by project name")
def list_repos(user, project):
    print("TODO")

@repo.command(name="status")
@click.option("--user", help="Filter by username")
@click.option("--project", help="Filter by project name")
def show_repo_progress():
    print("TODO")
