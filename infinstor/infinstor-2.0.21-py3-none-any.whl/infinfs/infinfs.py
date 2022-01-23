from __future__ import print_function
import os
import builtins
import json
import mlflow
from fuse import Operations
from urllib.parse import urlparse
import sys
from infinstor.infinfs import infin_download
import boto3
from infinstor import infin_boto3

verbose = False

def print_unbufferred(*args, **kwargs):
    if verbose:
        binary_args = []
        for arg in args:
            binary_args.append(str(arg).encode('utf-8'))
        print(*binary_args, file=sys.stderr, **kwargs)

class InfinFS(Operations):
    def __init__(self, mountpoint, input_spec, service_name):
        if not mountpoint.startswith("/"):
            raise('Mountpoint must be absolute path')
        self.mountpoint = mountpoint.rstrip("/")
        ##Load input specs if available
        self.infinstor_time_spec = None
        self.load_input_specs(input_spec, self.mountpoint, service_name)

        ##Create shadow location
        mountdir = os.path.dirname(self.mountpoint)
        mountbasename = os.path.basename(self.mountpoint)
        shadowbasename = ".infin-" + mountbasename + "-shadow"
        self.shadow_location = mountdir + "/" + shadowbasename
        if not os.path.exists(self.shadow_location):
            os.mkdir(self.shadow_location)
        print_unbufferred(self.prefix, self.mountpoint, self.shadow_location, self.bucket)

    def load_input_specs(self, specs, requested_mountpoint, service_name):
        print_unbufferred('specs ##')
        print_unbufferred(specs)
        if specs['type'] == 'infinsnap' or specs['type'] == 'infinslice':
            time_spec = specs.get('time_spec')
            bucket = specs['bucketname']
            prefix = specs['prefix']
            if time_spec:
                self.infinstor_time_spec = time_spec
            self.bucket = bucket
            if 'unsplitted_prefix' in specs:
                self.get_partition_mount_prefix(specs['unsplitted_prefix'], prefix,
                                                                 requested_mountpoint)
            else:
                self.prefix = prefix.lstrip('/').rstrip('/')
        elif specs['type'] == 'mlflow-run-artifacts':
            client = mlflow.tracking.MlflowClient()
            run = client.get_run(specs['run_id'])
            artifact_uri = run.info.artifact_uri
            parse_result = urlparse(artifact_uri)
            if (parse_result.scheme != 's3'):
                raise ValueError('Error. Do not know how to deal with artifacts in scheme ' \
                                 + parse_result.scheme)
            self.bucket = parse_result.netloc
            if 'unsplitted_prefix' in specs and 'prefix' in specs:
                self.get_partition_mount_prefix(specs['unsplitted_prefix'], specs['prefix'],
                                                                 requested_mountpoint)
            elif 'prefix' in specs:
                self.prefix = specs['prefix'].lstrip('/').rstrip('/')
            else:
                self.prefix = os.path.join(parse_result.path.lstrip('/'), "infinstor")

    def get_partition_mount_prefix(self, unsplitted_prefix, partition_prefix, requested_mountpoint):
        print_unbufferred("get_partition_mount_prefix ##")
        print_unbufferred(unsplitted_prefix, partition_prefix, requested_mountpoint)
        original_prefix = unsplitted_prefix.lstrip("/").rstrip("/")
        partition_prefix = partition_prefix.lstrip("/").rstrip("/")
        if original_prefix == partition_prefix:
            print_unbufferred('Partitioned prefix is same as unsplitted prefix')
            self.prefix = partition_prefix
            self.mountpoint = requested_mountpoint
        elif not original_prefix:
            print_unbufferred("Original prefix is empty")
            self.prefix = partition_prefix
            self.mountpoint = os.path.join(requested_mountpoint, partition_prefix)
            os.makedirs(self.mountpoint, exist_ok=True)
        elif partition_prefix.startswith(original_prefix):
            print_unbufferred("Extending prefix for partitioning")
            part = partition_prefix[len(original_prefix):].lstrip('/')
            self.mountpoint = os.path.join(requested_mountpoint, part)
            os.makedirs(self.mountpoint, exist_ok=True)
            self.prefix = partition_prefix
        else:
            raise Exception('Invalid partition prefix ')

    def get_mountpoint(self):
        return self.mountpoint

    def get_s3_client(self):
        if self.infinstor_time_spec:
            return boto3.client('s3', infinstor_time_spec=self.infinstor_time_spec)
        else:
            return boto3.client('s3')


    def get_bucket_prefix(self, s3path):
        m = urlparse(s3path)
        return m.netloc, m.path.lstrip('/').rstrip('/')

    def get_mount_relative_path(self, absolute_path):
        if self.mountpoint not in absolute_path:
            raise Exception("Invalid mounted path")
        rel_path = absolute_path[len(self.mountpoint):]
        return rel_path.lstrip('/')

    def get_remote_path(self, full_path):
        if not full_path.startswith(self.mountpoint):
            raise Exception("Invalid mounted path " + full_path)
        rel_path = self.get_mount_relative_path(full_path)
        if self.prefix and rel_path:
            return self.prefix + "/" + rel_path
        elif self.prefix:
            return self.prefix
        else:
            return rel_path

    def get_shadow_path(self, path):
        spath = self.shadow_location + path[len(self.mountpoint):]
        return spath


    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.mountpoint, partial)
        return path

    def get_file_type(self, s3_list_response):
        if 'CommonPrefixes' in s3_list_response:
            return 'directory'
        elif 'Contents' in s3_list_response:
            if len(s3_list_response['Contents']) > 1 \
                    or s3_list_response['Contents'][0]['Key'].endswith('/') \
                    or s3_list_response['Contents'][0]['Size'] == 0:
                return 'directory'
            else:
                return 'file'
        else:
            return None

    ##File Methods

    def readdir(self, path, fh):
        ##List operation
        full_path = self._full_path(path)
        prefix = self.get_remote_path(full_path)
        if prefix and os.path.isdir(full_path):
            prefix = prefix + '/'
        client = self.get_s3_client()
        print_unbufferred("readdir ## ", self.bucket, prefix)
        obj_list_response = client.list_objects_v2(Bucket=self.bucket, Prefix=prefix, Delimiter='/')
        print_unbufferred(obj_list_response)
        dirents = ['.', '..']
        if 'Contents' in obj_list_response:
            for key in obj_list_response['Contents']:
                remote_path = key['Key']
                rel_path = remote_path[len(prefix):].lstrip('/')
                if not rel_path or rel_path == '.infinstor':
                    continue
                dirents.append(rel_path)
        if 'CommonPrefixes' in obj_list_response:
            for key in obj_list_response['CommonPrefixes']:
                remote_path = key['Prefix'].rstrip('/')
                rel_path = remote_path[len(prefix):].lstrip('/')
                if not rel_path or rel_path == '.infinstor':
                    continue
                folder_path = os.path.join(full_path, rel_path)
                local_shadow_folder = self.get_shadow_path(folder_path)
                st = self.create_folder(local_shadow_folder)
                dirents.append(rel_path)
        print_unbufferred(dirents)
        for r in dirents:
            yield r

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def open(self, path, flags):
        full_path = self._full_path(path)
        local_shadow_path = self.get_shadow_path(full_path)
        if not os.path.exists(local_shadow_path):
            remote_path = self.get_remote_path(full_path)

            #Check for folder or download
            client = self.get_s3_client()
            obj_list_response = client.list_objects_v2(Bucket=self.bucket, Prefix=remote_path, Delimiter='/')
            ftype = self.get_file_type(obj_list_response)
            if ftype == 'directory':
                #This is a folder
                print_unbufferred(path, "is a folder")
                self.create_folder(local_shadow_path)
            elif ftype == 'file':
                print_unbufferred(path, "is a file")
                tmp_shadow_file = self.get_temporary_shadow_file(local_shadow_path, ".tmp")
                infin_download.download_objects(local_shadow_path, tmp_shadow_file, self.bucket,
                                            remote_path, self.infinstor_time_spec)
            else:
                return None
        return os.open(local_shadow_path, flags)

    def get_remote_ls(self, local_path):
        prefix = self.get_remote_path(local_path)
        print_unbufferred("#get_remote_ls# " + local_path, " Bucket = " + self.bucket + ", prefix = " + prefix)
        client = self.get_s3_client()
        obj_list_response = client.list_objects_v2(Bucket=self.bucket, Prefix=prefix, Delimiter='/')
        print_unbufferred(obj_list_response)
        return obj_list_response


    def release(self, path, fh):
        return os.close(fh)

    def statfs(self, path):
        stv = os.statvfs(self.shadow_location)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
                                                         'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files',
                                                         'f_flag',
                                                         'f_frsize', 'f_namemax'))

    def getattr(self, path, fh=None):
        print_unbufferred("Inside getattr path = " + path)
        if path == "/":
            st = os.lstat(self.shadow_location)
            return self.get_attr_from_lstat(st)
        full_path = self._full_path(path)
        local_shadow_path = self.get_shadow_path(full_path)
        temp_shadow_file = self.get_temporary_shadow_file(local_shadow_path, ".tmp")
        print_unbufferred(full_path, local_shadow_path, temp_shadow_file)
        if os.path.exists(local_shadow_path):
            st = os.lstat(local_shadow_path)
        elif os.path.exists(temp_shadow_file):
            st = os.lstat(temp_shadow_file)
        else:
            list_response = self.get_remote_ls(full_path)
            ftype = self.get_file_type(list_response)
            if ftype == "directory":
                st = self.create_folder(local_shadow_path)
            elif ftype == 'file':
                st, tmp_shadow_file = self.create_tmp_file(local_shadow_path, int(list_response['Contents'][0]['Size']))
            else:
                return dict()
        attr = self.get_attr_from_lstat(st)
        return attr

    def get_attr_from_lstat(self, st):
        stat = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                                        'st_uid'))
        return stat

    def create_folder(self, shadow_path):
        os.makedirs(shadow_path, exist_ok=True)
        return os.lstat(shadow_path)

    def get_temporary_shadow_file(self, local_shadow_path, suffix):
        basename = os.path.basename(local_shadow_path)
        dirname = os.path.dirname(local_shadow_path)
        tmp_shadow_file = dirname + "/.infin-" + basename + suffix
        return tmp_shadow_file

    def create_tmp_file(self, local_shadow_path, size=0):
        tmp_shadow_file = self.get_temporary_shadow_file(local_shadow_path, ".tmp")
        if not os.path.exists(tmp_shadow_file):
            with open(tmp_shadow_file, "w") as fh:
                fh.close()
            #Truncate to actual filesize
            #Note: when the download starts, the file size will be reset
            os.truncate(tmp_shadow_file, size)
        return os.lstat(tmp_shadow_file), tmp_shadow_file
    ## Following methods will do nothing,
    ## but, will not throw exception

    def flush(self, path, fh):
        ##Do Nothing
        pass

    def fsync(self, path, fdatasync, fh):
        ##Do Nothing
        pass

    ##Following methods are not supported
    ##Will throw exception

    def access(self, path, mode):
        ##Access is checked at S3
        return 0

    def chmod(self, path, mode):
        raise ('Not Supported')

    def chown(self, path, uid, gid):
        raise ('Not Supported')

    def readlink(self, path):
        raise('Not Supported')

    def mknod(self, path, mode, dev):
        raise('Not Supported')

    def rmdir(self, path):
        raise('Not Supported')

    def mkdir(self, path, mode):
        raise('Not Supported')

    def unlink(self, path):
        raise ('Not Supported')

    def symlink(self, name, target):
        raise ('Not Supported')

    def rename(self, old, new):
        raise ('Not Supported')

    def link(self, target, name):
        raise ('Not Supported')

    def utimens(self, path, times=None):
        raise ('Not Supported')

    def create(self, path, mode, fi=None):
        raise ('Not Supported')

    def write(self, path, buf, offset, fh):
        raise ('Not Supported')

    def truncate(self, path, length, fh=None):
        raise ('Not Supported')

