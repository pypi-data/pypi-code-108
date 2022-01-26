# Copyright 2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import gzip
import hashlib
import json
import os
import shutil
import tarfile
import tempfile

from six.moves.configparser import (
    NoOptionError,
    NoSectionError,
    )

from lpbuildd.debian import (
    DebianBuildManager,
    DebianBuildState,
    )
from lpbuildd.proxy import BuildManagerProxyMixin


RETCODE_SUCCESS = 0
RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


class OCIBuildState(DebianBuildState):
    BUILD_OCI = "BUILD_OCI"


class OCIBuildManager(BuildManagerProxyMixin, DebianBuildManager):
    """Build an OCI Image."""

    backend_name = "lxd"
    initial_build_state = OCIBuildState.BUILD_OCI

    @property
    def needs_sanitized_logs(self):
        return True

    def initiate(self, files, chroot, extra_args):
        """Initiate a build with a given set of files and chroot."""
        self.name = extra_args["name"]
        self.branch = extra_args.get("branch")
        self.git_repository = extra_args.get("git_repository")
        self.git_path = extra_args.get("git_path")
        self.build_file = extra_args.get("build_file")
        self.build_args = extra_args.get("build_args", {})
        self.build_path = extra_args.get("build_path")
        self.proxy_url = extra_args.get("proxy_url")
        self.revocation_endpoint = extra_args.get("revocation_endpoint")
        self.proxy_service = None

        super(OCIBuildManager, self).initiate(files, chroot, extra_args)

    def doRunBuild(self):
        """Run the process to build the OCI image."""
        args = []
        args.extend(self.startProxy())
        if self.revocation_endpoint:
            args.extend(["--revocation-endpoint", self.revocation_endpoint])
        if self.branch is not None:
            args.extend(["--branch", self.branch])
        if self.git_repository is not None:
            args.extend(["--git-repository", self.git_repository])
        if self.git_path is not None:
            args.extend(["--git-path", self.git_path])
        if self.build_file is not None:
            args.extend(["--build-file", self.build_file])
        if self.build_args:
            for k, v in self.build_args.items():
                args.extend(["--build-arg", "%s=%s" % (k, v)])
        if self.build_path is not None:
            args.extend(["--build-path", self.build_path])
        try:
            snap_store_proxy_url = self._builder._config.get(
                "proxy", "snapstore")
            args.extend(["--snap-store-proxy-url", snap_store_proxy_url])
        except (NoSectionError, NoOptionError):
            pass
        args.append(self.name)
        self.runTargetSubProcess("build-oci", *args)

    def iterate_BUILD_OCI(self, retcode):
        """Finished building the OCI image."""
        self.stopProxy()
        self.revokeProxyToken()
        if retcode == RETCODE_SUCCESS:
            print("Returning build status: OK")
            return self.deferGatherResults()
        elif (retcode >= RETCODE_FAILURE_INSTALL and
              retcode <= RETCODE_FAILURE_BUILD):
            if not self.alreadyfailed:
                self._builder.buildFail()
                print("Returning build status: Build failed.")
            self.alreadyfailed = True
        else:
            if not self.alreadyfailed:
                self._builder.builderFail()
                print("Returning build status: Builder failed.")
            self.alreadyfailed = True
        self.doReapProcesses(self._state)

    def iterateReap_BUILD_OCI(self, retcode):
        """Finished reaping after building the OCI image."""
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()

    def _calculateLayerSha(self, layer_path):
        with open(layer_path, 'rb') as layer_tar:
            sha256_hash = hashlib.sha256()
            for byte_block in iter(lambda: layer_tar.read(4096), b""):
                sha256_hash.update(byte_block)
            digest = sha256_hash.hexdigest()
            return digest

    def _gatherManifestSection(self, section, extract_path, sha_directory):
        config_file_path = os.path.join(extract_path, section["Config"])
        self._builder.addWaitingFile(config_file_path)
        with open(config_file_path, 'r') as config_fp:
            config = json.load(config_fp)
        diff_ids = config["rootfs"]["diff_ids"]
        digest_diff_map = {}
        for diff_id, layer_id in zip(diff_ids, section['Layers']):
            layer_id = layer_id.split('/')[0]
            diff_file = os.path.join(sha_directory, diff_id.split(':')[1])
            layer_path = os.path.join(
                extract_path, "{}.tar.gz".format(layer_id))
            self._builder.addWaitingFile(layer_path)
            # If we have a mapping between diff and existing digest,
            # this means this layer has been pulled from a remote.
            # We should maintain the same digest to achieve layer reuse
            if os.path.exists(diff_file):
                with open(diff_file, 'r') as diff_fp:
                    diff = json.load(diff_fp)
                    # We should be able to just take the first occurence,
                    # as that will be the 'most parent' image
                    digest = diff[0]["Digest"]
                    source = diff[0]["SourceRepository"]
            # If the layer has been build locally, we need to generate the
            # digest and then set the source to empty
            else:
                source = ""
                digest = self._calculateLayerSha(layer_path)
            digest_diff_map[diff_id] = {
                "digest": digest,
                "source": source,
                "layer_id": layer_id
            }

        return digest_diff_map

    def gatherResults(self):
        """Gather the results of the build and add them to the file cache."""
        extract_path = tempfile.mkdtemp(prefix=self.name)
        try:
            proc = self.backend.run(
                ['docker', 'save', self.name],
                get_output=True, return_process=True)
            tar = tarfile.open(fileobj=proc.stdout, mode="r|")
        except Exception as e:
            self._builder.log("Unable to save image: {}".format(e))
            raise

        current_dir = ''
        gzip_layer = None
        symlinks = []
        try:
            # The tarfile is a stream and must be processed in order
            for file in tar:
                self._builder.log("Processing tar file: {}".format(file.name))
                # Directories are just nodes, you can't extract the children
                # directly, so keep track of what dir we're in.
                if file.isdir():
                    current_dir = file.name
                    if gzip_layer:
                        # Close the old directory if we have one
                        gzip_layer.close()
                if file.issym():
                    # symlinks can't be extracted or derefenced from a stream
                    # as you can't seek backwards.
                    # Work out what the symlink is referring to, then
                    # we can deal with it later
                    self._builder.log(
                        "Found symlink at {} referencing {}".format(
                            file.name, file.linkpath))
                    symlinks.append(file)
                    continue
                if current_dir and file.name.endswith('layer.tar'):
                    # This is the actual layer data.
                    # Instead of adding the layer.tar to a gzip directory
                    # we add the contents of untarred layer.tar to a gzip.
                    # Now instead of having a gz directory in the form:
                    # directory.tar.gz/layer.tar/contents
                    # we will have: layer.tar.gz/contents. This final gz format
                    # will have to have the name of the directory
                    # (directory_name.tar.gz/contents) otherwise we will endup
                    # with multiple gzips with the same name "layer.tar.gz".
                    fileobj = tar.extractfile(file)
                    name = os.path.join(extract_path,
                                        '{}.tar.gz'.format(current_dir))
                    with gzip.GzipFile(name, 'wb') as gzip_layer:
                        byte = fileobj.read(1)
                        while len(byte) > 0:
                            gzip_layer.write(byte)
                            byte = fileobj.read(1)
                elif current_dir and file.name.startswith(current_dir):
                    # Other files that are in the layer directories,
                    # we don't care about
                    continue
                else:
                    # If it's not in a directory, we need that
                    tar.extract(file, extract_path)
        except Exception as e:
            self._builder.log("Tar file processing failed: {}".format(e))
            raise
        finally:
            if gzip_layer is not None:
                gzip_layer.close()
            fileobj.close()

        # deal with any symlinks we had
        for symlink in symlinks:
            # These are paths that finish in "<layer_id>/layer.tar"
            # we want the directory name, which should always be
            # the second component
            source_name = os.path.join(
                extract_path,
                "{}.tar.gz".format(symlink.linkpath.split('/')[-2]))
            target_name = os.path.join(
                extract_path,
                '{}.tar.gz'.format(symlink.name.split('/')[-2]))
            # Do a copy to dereference the symlink
            self._builder.log(
                "Deferencing symlink from {} to {}".format(
                    source_name, target_name))
            shutil.copy(source_name, target_name)

        # We need these mapping files
        sha_directory = tempfile.mkdtemp()
        # This can change depending on the kernel options / docker package
        # used. This is correct for bionic buildd image
        # with apt installed docker.
        sha_path = ('/var/lib/docker/image/'
                    'vfs/distribution/v2metadata-by-diffid/sha256')
        # If there have been no images pulled in the build process
        # (FROM scratch), then this directory will not exist and
        # we will have no contents from it.
        if self.backend.path_exists(sha_path):
            sha_files = [x for x in self.backend.listdir(sha_path)
                         if not x.startswith('.')]
            for file in sha_files:
                self.backend.copy_out(
                    os.path.join(sha_path, file),
                    os.path.join(sha_directory, file)
                )
        else:
            self._builder.log("No metadata directory at {}".format(sha_path))

        # Parse the manifest for the other files we need
        manifest_path = os.path.join(extract_path, 'manifest.json')
        self._builder.addWaitingFile(manifest_path)
        with open(manifest_path) as manifest_fp:
            manifest = json.load(manifest_fp)

        digest_maps = []
        try:
            for section in manifest:
                digest_maps.append(
                    self._gatherManifestSection(section, extract_path,
                                                sha_directory))
            digest_map_file = os.path.join(extract_path, 'digests.json')
            with open(digest_map_file, 'w') as digest_map_fp:
                json.dump(digest_maps, digest_map_fp)
            self._builder.addWaitingFile(digest_map_file)
        except Exception as e:
            self._builder.log("Failed to parse manifest: {}".format(e))
            raise
