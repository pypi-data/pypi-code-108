import os
import sys
#import json
import click
import logging
import asana

logger = logging.getLogger(__name__)

# TODO: add this to a --verbose parameter.
#       global verbose parameter is hard in Click
#       see https://github.com/pallets/click/issues/108
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('requests').setLevel(logging.WARNING)
# logging.getLogger('urllib3').setLevel(logging.WARNING)

try:
    ASANA_TOKEN = os.environ['ASANA_TOKEN']
except KeyError:
    print("environment variable ASANA_TOKEN is not set", file=sys.stderr)
    sys.exit(1)

# setup client that accesses all resources
client = asana.Client.access_token(ASANA_TOKEN)
# each client request now contains name of client
client.options['client_name'] = "asana-cli"

me = client.users.me()

def get_item(item_type, items, name):
    try:
        return [x for x in items if x['name'] == name][0]
    except IndexError:
        print(f"unable to find {item_type} {name}", file=sys.stderr)
        sys.exit(1)

def get_project(name, workspace):
    projects = client.projects.get_projects_for_workspace(workspace['gid'])
    return get_item("project", projects, name)

def get_section(name, project):
    sections = client.sections.get_sections_for_project(project['gid'])
    return get_item("section", sections, name)

def get_tasks(project, section=None):
    if section:
        tasks = client.tasks.get_tasks_for_section(section['gid'])
    else:
        tasks = client.tasks.get_tasks_for_project(project['gid'])
    return tasks

@click.group()
def main():
    """
    \b
    Examples:

    \b
    asana list workspaces
    asana list projects --workspace="Personal Projects"
    asana list tasks --workspace="Personal Projects" --project="Test"
    asana list sections --workspace="Personal Projects" --project="Test"
    asana list tasks --workspace="Personal Projects" --project="Test" --section="Column 1"

    \b
    asana delete tasks --workspace="Personal Projects" --project="Test" --section="Column 1"

    \b
    asana mark tasks --workspace="Personal Projects" --project="Test" --section="Column 1" --completed
    asana mark tasks --workspace="Personal Projects" --project="Test" --section="Column 1" --not-completed

    \b
    asana move tasks --workspace="Personal Projects" --from-project="Test" --from-section="Column 1" --to-section="Column 2"
    """
    pass

# ---------------------------------
# list

@main.group(name='list')
def list_():
    pass

@list_.command(name='workspaces')
def list_workspaces():
    workspaces = me['workspaces']
    for workspace in workspaces:
        print(workspace)
        #print(json.dumps(workspace))

@list_.command(name='projects')
@click.option('--workspace', required=True)
def list_projects(workspace):
    workspace_obj = get_item("workspace", me['workspaces'], workspace)
    projects = client.projects.get_projects_for_workspace(workspace_obj['gid'])
    for project in projects:
        print(project)
        #print(json.dumps(project))

@list_.command(name='sections')
@click.option('--workspace', required=True)
@click.option('--project', required=True)
def list_sections(workspace, project):
    workspace_obj = get_item("workspace", me['workspaces'], workspace)
    project_obj = get_project(project, workspace=workspace_obj)
    sections = client.sections.get_sections_for_project(project_obj['gid'])
    for section in sections:
        print(section)
        #print(json.dumps(section))

@list_.command(name='tasks')
@click.option('--workspace', required=True)
@click.option('--project', required=True)
@click.option('--section')
def list_tasks(workspace, project, section):
    workspace_obj = get_item("workspace", me['workspaces'], workspace)
    project_obj = get_project(project, workspace=workspace_obj)
    section_obj = get_section(section, project=project_obj) if section else None
    tasks = get_tasks(project_obj, section=section_obj)
    for task in tasks:
        print(task)
        #print(json.dumps(task))

# ---------------------------------
# move

@main.group()
def move():
    pass

def move_tasks_inner(source_project, source_section, target_project, target_section):
    """
    move tasks from source to target
    """
    source_project_gid, source_project_name = source_project['gid'], source_project['name']
    source_section_gid, source_section_name = source_section['gid'], source_section['name']
    target_project_gid, target_project_name = target_project['gid'], target_project['name']
    target_section_gid, target_section_name = target_section['gid'], target_section['name']

    source_tasks = client.tasks.get_tasks_for_section(source_section_gid)

    if len(source_tasks) == 0:
        print(f"no tasks to move in section {source_section_name} of project {source_project_name}")

    for task in source_tasks:
        task_gid = task['gid']
        if source_project_gid == target_project_gid:
            print(f"moving task {task_gid} from {source_section_name} to {target_section_name} "
                  f"within project {target_project_name}", end="...")
        else:
            print(f"moving task {task_gid} from {source_section_name} in {source_project_name} "
                                          f"to {target_section_name} in {target_project_name}", end="...")
        response = client.tasks.add_project_for_task(task_gid, {"project": target_project_gid, "section": target_section_gid})
        if response.status_code != 200:
            print(f"failed")
            sys.exit(1)
        else:
            print(f"success!")

@move.command(name='tasks')
@click.option('--workspace', required=True)
@click.option('--from-project', required=True)
@click.option('--from-section', required=True)
@click.option('--to-project')
@click.option('--to-section', required=True)
def move_tasks(workspace, from_project, from_section, to_project, to_section):
    workspace_obj = get_item("workspace", me['workspaces'], workspace)
    from_project_obj = get_project(from_project, workspace=workspace_obj)
    from_section_obj = get_section(from_section, project=from_project_obj)
    to_project_obj = get_project(to_project, workspace=workspace_obj) if to_project else from_project_obj
    to_section_obj = get_section(to_section, project=to_project_obj)

    move_tasks_inner(from_project_obj, from_section_obj, to_project_obj, to_section_obj)

# ---------------------------------
# delete

@main.group()
def delete():
    pass

@delete.command(name='tasks')
@click.option('--workspace', required=True)
@click.option('--project', required=True)
@click.option('--section', required=True)
def delete_tasks(workspace, project, section):
    workspace_obj = get_item("workspace", me['workspaces'], workspace)
    project_obj = get_project(project, workspace=workspace_obj)
    section_obj = get_section(section, project=project_obj)
    tasks = get_tasks(project_obj, section=section_obj)
    for task in tasks:
        task_gid = task['gid']
        print(f"deleting {task_gid}", end="...")
        response = client.tasks.delete_task(task_gid)
        if response.status_code != 200:
            print(f"failed")
            sys.exit(1)
        else:
            print(f"success")

# ---------------------------------
# mark

@main.group()
def mark():
    pass

@mark.command(name='tasks')
@click.option('--workspace', required=True)
@click.option('--project', required=True)
@click.option('--section', required=True)
@click.option('--completed/--not-completed', default=True)
def mark_tasks(workspace, project, section, completed):
    workspace_obj = get_item("workspace", me['workspaces'], workspace)
    project_obj = get_project(project, workspace=workspace_obj)
    section_obj = get_section(section, project=project_obj)
    tasks = get_tasks(project_obj, section=section_obj)
    for task in tasks:
        task_gid = task['gid']
        complete_or_incomplete = "complete" if completed else "incomplete"
        print(f"marking {task_gid} as {complete_or_incomplete}", end="...")
        response = client.tasks.update_task(task_gid, {"completed": completed})
        if response.status_code != 200:
            print(f"failed")
            sys.exit(1)
        else:
            print(f"success")

if __name__ == "__main__":
    main()
