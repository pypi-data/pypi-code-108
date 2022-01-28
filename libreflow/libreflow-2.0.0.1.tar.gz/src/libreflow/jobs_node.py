import sys
import argparse
import os

from libreflow.session import JobsNodeSession


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Session Arguments'
    )
    parser.add_argument(
        '-r', '--root_dir', dest='root_dir'
    )
    parser.add_argument(
        '-s', '--site', default='LFS', dest='site'
    )
    parser.add_argument(
        '--blender_exec_path', dest='blender_exec_path'
    )
    values, remaining_args = parser.parse_known_args(args)

    if values.root_dir:
        os.environ["ROOT_DIR"] = values.root_dir
    if values.site:
        os.environ["KABARET_SITE_NAME"] = values.site
    if values.blender_exec_path:
        os.environ["BLENDER_EXEC_PATH"] = values.blender_exec_path
    
    return remaining_args


if __name__ == '__main__':
    argv = sys.argv[1:]  # get ride of first args wich is script filename
    session_name, host, port, cluster_name, db, password, debug, remaining_args \
        = JobsNodeSession.parse_command_line_args(argv)
    pools = process_remaining_args(remaining_args)
    if not pools:
        print('\n!!!\nUsage:', sys.argv[0], 'pool_name pool_name ...\n\n')
    else:
        node = JobsNodeSession(pools, session_name=session_name, debug=debug)
        node.cmds.Cluster.connect(host, port, cluster_name, db, password)

        node.wait_for_jobs()
        print('Jobs Node closed.')
        
