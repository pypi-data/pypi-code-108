# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import os
import paramiko
import scp
import shutil
import tempfile

from yangsuite import get_path


scp_status = {}
"""Dict of per-user {value, max, info} dicts for SCP operations in progress."""


def scp_files_to_repository(host, targetrepo, user,
                            username, password,
                            remote_paths=None,
                            include_subdirs=False):
    """SCP files from the given remote directory to a repository.

    Args:
      host (str): Hostname or IP address to copy from
      targetrepo (YSYangRepository): Existing repository to add files to
      user (str): YANG Suite username (used for scp_status entry)
      username (str): Remote host username
      password (str): Remote host password
      remote_paths (list): Path(s) on remote host to copy from
      include_subdirs (bool): Whether to recurse into subdirectories on the
        remote host and copy files found there as well.

    Returns:
      dict: ``{status: (error status code), reason}`` or
      ``{status: 200, result}``.
    """
    scp_status[user] = {
        'value': 0,
        'max': 0,
        'info': "Preparing...",
    }

    scratchdir = tempfile.mkdtemp(dir=get_path('scratch', user=user))
    try:
        with paramiko.SSHClient() as sshc:
            # Add new host keys, instead of rejecting as unknown
            sshc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshc.connect(host,
                         username=username,
                         password=password,
                         timeout=30)

            # Get the files to copy
            files_to_copy = []
            for remote_path in remote_paths:
                # TODO: this assumes the remote host is a Mac or Linux system,
                # and will fail if it's a Windows system or something.
                if include_subdirs:
                    sin, sout, serr = sshc.exec_command(
                        'find ' + remote_path + ' -name *.yang')
                else:
                    sin, sout, serr = sshc.exec_command(
                        'ls -1 ' + remote_path + '/*.yang')

                files = sout.read().decode('utf-8').strip().split("\n")
                # Each entry is (remote_path, relative_path_to_file)
                files = [(remote_path, f[len(remote_path) + 1:])
                         for f in files if f]
                files_to_copy += files

            scp_status[user]['max'] = len(files_to_copy)

            if not files_to_copy:
                return {'status': 404, 'reason': "No files to copy"}

            # Establish SCP session over the SSH session
            with scp.SCPClient(sshc.get_transport()) as scpc:
                for (remote_path, rel_path) in files_to_copy:
                    file_path = "{0}/{1}".format(remote_path, rel_path)
                    scp_status[user]['info'] = "Copying " + rel_path + "..."
                    dest_path = os.path.join(scratchdir,
                                             os.path.normcase(rel_path))
                    dest_dir = os.path.dirname(dest_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    scpc.get(remote_path=file_path, local_path=dest_path)
                    scp_status[user]['value'] += 1

            scp_status[user]['info'] = "Adding files to YANG repository..."

            result = targetrepo.add_yang_files(scratchdir,
                                               include_subdirs=include_subdirs)
            return {'status': 200, 'result': result}

    except paramiko.ssh_exception.AuthenticationException:
        return {'status': 401, 'reason': "Authentication failed"}

    except (paramiko.ssh_exception.SSHException,
            paramiko.ssh_exception.NoValidConnectionsError,
            scp.SCPException) as exc:
        return {'status': 500, 'reason': str(exc)}

    finally:
        if os.path.exists(scratchdir):
            shutil.rmtree(scratchdir, ignore_errors=True)
        if user in scp_status:
            del scp_status[user]


def scp_files_from_xe_workspace(*args, ws_root=None):
    """Copy YANG modules from an XE workspace.

    Args:
      *args: See :func:`scp_files_to_repository`.
      ws_root (str): Path on remote server to root of IOS XE workspace.
    """
    if not ws_root.endswith("/"):
        ws_root = ws_root + "/"
    yang_root = ws_root + "binos/mgmt/dmi/model/yang/src/"
    return scp_files_to_repository(*args, remote_paths=[
        # yang_root + "compat" is intentionally excluded
        yang_root + "constraint",
        yang_root + "ddmi",
        yang_root + "ddmi-sync/acl",
        yang_root + "dsl",
        yang_root + "ietf",
        yang_root + "mdt",
        yang_root + "ned",
        # yang_root + "ned/cedge" is intentionally excluded
        yang_root + "openconfig",
        yang_root + "self-management",
        ws_root + "binos/mgmt/confd/confd/confd_x86_64/src/confd/yang",
    ], include_subdirs=False)
