import os


def data_upload(host, port, username, keyfile, local_dir, remote_dir):
    if local_dir.endswith(os.sep):
        local_dir = local_dir[:-1]
    os.system("rsync -az --delete --rsh='ssh -p {} -i {} -o ForwardX11=no' {}/ {}@{}:~/{}".format(
        port, keyfile, local_dir, username, host, remote_dir,
    ))


#def ftp_upload_dir(host, username, password, local_dir, remote_dir):
#    sf = ftputil.session.session_factory(
#        base_class=ftplib.FTP,
#        port=21,
#        use_passive_mode=False
#    )
#    local_dir = local_dir.strip(os.sep)
#    with ftputil.FTPHost(host, username, password, session_factory=sf) as ftp:
#        for base, dirs, files in os.walk(local_dir):
#            remote_base = base.replace(local_dir, remote_dir)
#
#            if not ftp.path.exists(remote_base):
#                ftp.mkdir(remote_base)
#
#            for f in files:
#                local_f = os.path.join(base, f)
#                remote_f = ftp.path.join(remote_base, f)
#                ftp.upload(local_f, remote_f)
#

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
