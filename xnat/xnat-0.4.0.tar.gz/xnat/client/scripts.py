import click
import xnat

from time import sleep

from ..scripts.copy_project import XNATProjectCopier
from ..scripts.data_integrity_check import XNATIntegrityCheck


@click.group(name="script")
def script():
    """
    Collection of various XNAT-related scripts.
    """
    pass


@script.command()
@click.option("--source-host", required=True, help="Source XNAT URL")
@click.option("--source-project", required=True, help="Source XNAT project")
@click.option("--dest-host", required=True, help="Destination XNAT URL")
@click.option("--dest-project", required=True, help="Destination XNAT project")
def copy_project(source_host, source_project, dest_host, dest_project):
    """Copy all data from source project to destination project. Source and destination projects can be located in different XNAT instances."""
    with xnat.connect(source_host) as source_xnat, xnat.connect(dest_host) as dest_xnat:
        # Find projects
        try:
            source_project = source_xnat.projects[source_project]
            dest_project = dest_xnat.projects[dest_project]
        except KeyError as error:
            print(error.message)
        else:
            # Create and start copier
            copier = XNATProjectCopier(source_xnat, source_project, dest_xnat, dest_project)
            copier.start()


@script.command()
@click.option("--host", required=True, help="XNAT URL")
@click.option("--xnat-home-dir", required=True, help="Path to XNAT home directory")
@click.option("--report", required=True, help="Path to report file")
def data_integrity_check(host, xnat_home_dir, report):
    """Perform data integrity check."""
    xnat_integrity_checker = XNATIntegrityCheck(host, xnat_home_dir)
    xnat_integrity_checker.start()
    print('progress\t FS\tXNAT')
    while xnat_integrity_checker.is_running():
        xnat_progress, fs_progress = xnat_integrity_checker.progress()
        print(f'\t\t{fs_progress*100}\t{xnat_progress*100}', end='\r')
        sleep(1)
    fs_progress, xnat_progress = xnat_integrity_checker.progress()
    print(f'\t\t{fs_progress*100}\t{xnat_progress*100}')
    print("--- REPORT ---")
    xnat_integrity_checker.write_report(report)
    print('--- DONE ---')
