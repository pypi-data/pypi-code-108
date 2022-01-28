import os
import sys
import argparse
import time

from .session import BaseCLISession


def parse_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Synchronization Session Arguments'
    )
    parser.add_argument(
        '-s', '--site', default='LFS', dest='site'
    )
    parser.add_argument(
        '-p', '--project', dest='project'
    )
    values, _ = parser.parse_known_args(args)

    return (
        values.site,
        values.project
    )


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        remaining_args,
    ) = BaseCLISession.parse_command_line_args(argv)

    session = BaseCLISession(session_name=session_name, debug=debug)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password)

    (
        site,
        project
    ) = parse_remaining_args(remaining_args)

    session.cmds.Flow.call(
        "/" + project,
        "ensure_runners_loaded",
        args={}, kwargs={}
    )

    if site:
        os.environ["KABARET_SITE_NAME"] = site
    
    site_oid = "/%s/admin/sites/%s" % (project, site)
    sync_action = "/%s/admin/process_jobs" % project
    job_queue_oid = site_oid + "/queue"

    exchange_site = session.cmds.Flow.call(
        "/" + project, "get_exchange_site",
        args={}, kwargs={}
    )
    
    get_next_waiting_job = lambda qid: session.cmds.Flow.call(
        qid, "get_next_waiting_job", args={}, kwargs={}
    )
    synchronize_job = lambda job: session.cmds.Flow.call(
        sync_action, "_process", args={job}, kwargs={}
    )
    set_revision_sync_status = lambda oid, status, site_name=None: session.cmds.Flow.call(
        oid, "set_sync_status", args={status}, kwargs=dict(site_name=site_name)
    )
    touch = lambda oid: session.cmds.Flow.call(
        oid, "touch", args={}, kwargs={}
    )

    while (True):
        job = get_next_waiting_job(job_queue_oid)

        if job:
            synchronize_job(job)
        
        time.sleep(1)

        if job and job.status.get() == "PROCESSED":
            if job.type.get() == "Download":
                set_revision_sync_status(job.emitter_oid.get(), "Available")
            elif job.type.get() == "Upload":
                set_revision_sync_status(job.emitter_oid.get(), "Available", exchange_site.name())
            
            touch(session.cmds.Flow.resolve_path(job.emitter_oid.get() + "/.."))


if __name__ == "__main__":
    main(sys.argv[1:])
