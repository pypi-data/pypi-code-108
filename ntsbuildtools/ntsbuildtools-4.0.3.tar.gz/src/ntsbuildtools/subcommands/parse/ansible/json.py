"""Parses Ansible JSON output and turns it into pretty Markdown output.

Reports on any failures. Optionally reports the 'diffs' for any number of 'crucial tasks'"""
from typing import List
import configargparse

import ntsbuildtools.io
from ntsbuildtools.markdown.comments import MarkdownComment
from ntsbuildtools.ansible.playbook.results import PlaybookResults


def main(args):
    # Parse the json output into a PlaybookResults object
    json_output = ntsbuildtools.io.readfile(args.src)
    results = PlaybookResults.from_json(json_output)

    markdown = render_playbook_result(
        results, args.crucial_task, args.crucial_task_type)

    with open(args.dst, 'w') as dst_file:
        dst_file.write(markdown)


def render_playbook_result(results: PlaybookResults,
                           crucial_tasks: List[str] = None,
                           crucial_ansible_modules: List[str] = None) -> str:
    markdown = MarkdownComment()
    for task_name in results.tasks:
        for task_result in results.by_task_name(task_name):
            if task_result.failed:
                markdown.add_message(task_result.as_markdown())
            elif crucial_tasks and task_result.task_name in crucial_tasks:
                markdown.add_message(task_result.as_markdown())
            elif crucial_ansible_modules and task_result.ansible_module in crucial_ansible_modules:
                markdown.add_message(task_result.as_markdown())
    return str(markdown)


def config_parser(parser: configargparse.ArgParser):
    parser.add_argument(
        'src',
        help='''Path to a Ansible JSON output file. This JSON file should be generated 
                using the "ansible.posix.json" Callback Plugin. (https://docs.ansible.com/ansible/latest/collections/ansible/posix/json_callback.html)'''
    )
    parser.add_argument(
        'dst',
        help='''Path to a file where the output should be saved. 
                NOTE: If the file exists, it's contents will be overwritten.'''
    )
    parser.add_argument(
        '--crucial-task', action='append',
        help="Any particular tasks that should ALWAYS be reported on. Provide the full name of that task."
    )
    parser.add_argument(
        '--crucial-task-type', action='append',
        help="""Often there will be one particular type of task that you want to see any results from. If there are any particular Ansible Modules that you'd like to see the results of, provide  type of task If there is one type of task that we should ALWAYS report on, provide its name here."""
    )
