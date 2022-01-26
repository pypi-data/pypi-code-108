import io
import json
import os
import tempfile
import tarfile


class OCITarball:
    """Create a tarball for use in tests with OCI."""

    def _makeFile(self, contents, name):
        json_contents = json.dumps(contents).encode("UTF-8")
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(json_contents)
        return tarinfo, io.BytesIO(json_contents)

    @property
    def config(self):
        return self._makeFile(
            {"rootfs": {
                "diff_ids": [
                    "sha256:diff1", "sha256:diff2", "sha256:diff3"]}},
            'config.json')

    @property
    def manifest(self):
        return self._makeFile(
            [{"Config": "config.json",
              "Layers": [
                  "layer-1/layer.tar",
                  "layer-2/layer.tar",
                  "layer-3/layer.tar"]}],
            'manifest.json')

    @property
    def repositories(self):
        return self._makeFile([], 'repositories')

    def layer_file(self, directory, layer_name):
        layer_directory = os.path.join(directory, layer_name)
        os.mkdir(layer_directory)
        contents = "{}-contents".format(layer_name)
        tarinfo = tarfile.TarInfo(contents)
        tarinfo.size = len(contents)
        layer_contents = io.BytesIO(contents.encode("UTF-8"))
        layer_tar_path = os.path.join(
            layer_directory, 'layer.tar')
        layer_tar = tarfile.open(layer_tar_path, 'w')
        layer_tar.addfile(tarinfo, layer_contents)
        layer_tar.close()
        return layer_directory

    def add_symlink_layer(self, directory, source_layer, target_layer):
        target_layer_directory = os.path.join(directory, target_layer)
        source_layer_directory = os.path.join(directory, source_layer)

        target = os.path.join(target_layer_directory, "layer.tar")
        source = os.path.join(source_layer_directory, "layer.tar")

        os.mkdir(target_layer_directory)
        os.symlink(os.path.relpath(source, target_layer_directory), target)
        return target_layer_directory

    def build_tar_file(self):
        tar_directory = tempfile.mkdtemp()
        tar_path = os.path.join(tar_directory, 'test-oci-image.tar')
        tar = tarfile.open(tar_path, 'w')
        tar.addfile(*self.config)
        tar.addfile(*self.manifest)
        tar.addfile(*self.repositories)

        for layer_name in ['layer-1', 'layer-2']:
            layer = self.layer_file(tar_directory, layer_name)
            tar.add(layer, arcname=layer_name)

        # add a symlink for 'layer-3'
        target_layer = self.add_symlink_layer(
            tar_directory, 'layer-2', 'layer-3')
        tar.add(target_layer, arcname="layer-3")

        tar.close()

        return tar_path
