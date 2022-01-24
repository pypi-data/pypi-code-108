# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import hashlib
import os
from azureml._project.ignore_file import get_project_ignore_file
from azureml._base_sdk_common.merkle_tree import create_merkletree


class _ModuleBuilder(object):
    """Create a _ModuleBuilder

    :param context: context object
    :type context: azureml.pipeline.core._GraphContext
    :param module_def: module def object
    :type module_def: ModuleDef
    :param snapshot_root: folder path that contains the script and other files of module.
        Place .amlignore or .gitignore file of your module here. All paths listed
        in .amlignore or .gitignore will be excluded from snapshot and hashing.
    :type snapshot_root: str
    :param existing_snapshot_id: guid of an existing snapshot. Specify this if the module wants to
        point to an existing snapshot.
    :type existing_snapshot_id: str
    :param arguments: annotated argument list
    :type arguments: list
    """

    def __init__(self, context, module_def, snapshot_root=None, existing_snapshot_id=None, arguments=None):
        """Initializes _ModuleBuilder."""
        if snapshot_root is not None:
            self._content_path = os.path.abspath(snapshot_root)
        else:
            self._content_path = snapshot_root
        self._module_provider = context.workflow_provider.module_provider
        self._module_def = module_def
        self._existing_snapshot_id = existing_snapshot_id
        self._arguments = arguments

    def get_fingerprint(self):
        """
        Calculate and return a deterministic unique fingerprint for the module
        :return: fingerprint
        :rtype str
        """
        fingerprint = _ModuleBuilder.calculate_hash(self._module_def, self._content_path)
        return fingerprint

    def build(self):
        """
        Build the module and register it with the provider
        :return: module_id
        :rtype str
        """
        fingerprint = self.get_fingerprint()

        if self._existing_snapshot_id:
            module_id = self._module_provider.create_module(
                module_def=self._module_def, existing_snapshot_id=self._existing_snapshot_id, fingerprint=fingerprint,
                arguments=self._arguments)
        else:
            module_id = self._module_provider.create_module(
                module_def=self._module_def, content_path=self._content_path, fingerprint=fingerprint,
                arguments=self._arguments)

        return module_id

    @property
    def module_def(self):
        return self._module_def

    @staticmethod
    def _flatten_hash_paths(hash_paths, content_path=None):
        all_paths = set()

        for hash_path in hash_paths:
            if os.path.exists(hash_path):
                all_paths.add(hash_path)
            elif content_path and os.path.exists(os.path.join(content_path, hash_path)):
                all_paths.add(os.path.join(content_path, hash_path))
            else:
                raise ValueError(
                    "path not found %s. Specify absolute paths or a path relative to the `source_directory`"
                    % hash_path)

        return list(all_paths)

    @staticmethod
    def _hash_from_file_paths(hash_src, root_path):
        from azureml._restclient.constants import SNAPSHOT_MAX_SIZE_BYTES, ONE_MB

        if len(hash_src) == 0:
            hash = "00000000000000000000000000000000"
        else:
            hasher = hashlib.md5()
            for f in hash_src:
                # Include the filename as part of the hash to account for renamed files
                name_to_hash = f
                if root_path and name_to_hash.startswith(root_path):
                    name_to_hash = os.path.relpath(name_to_hash, root_path)
                hasher.update(name_to_hash.encode('utf-8'))

                # Verify that this file can fit in a snapshot before we read it into memory
                if os.path.getsize(f) > SNAPSHOT_MAX_SIZE_BYTES:
                    msg = (
                        "File '%s' from source_directory exceeds the maximum snapshot size of %d MB.\n"
                        "Please use a separate directory for a step with files only related to that step.\n"
                        "If you didn't specify source_directory, it will use your working directory"
                        " and upload all files in that directory." % (f, SNAPSHOT_MAX_SIZE_BYTES / ONE_MB)
                    )
                    raise Exception(msg)

                # Hash the file contents
                with open(str(f), 'rb') as afile:
                    buf = afile.read()
                    hasher.update(buf)
            hash = hasher.hexdigest()
        return hash

    @staticmethod
    # The create_merkletree function outputs a tree structure.  Convert this to a flat list of files.
    def populate_paths_from_merkletree(root, paths, prefix):
        current_path = os.path.join(prefix, root.name)
        if root.is_file():
            paths.append(current_path)
        for child in root.children:
            _ModuleBuilder.populate_paths_from_merkletree(child, paths, current_path)

    @staticmethod
    def _default_content_hash_calculator(exclude_function=None, root_path=None):
        # Generate the set of files to include in the module hash, using the same merkle tree generation
        # code that the snaphshot client uses
        merkle_paths = []
        if root_path is not None:
            merkletree_root = create_merkletree(root_path, exclude_function)
            _ModuleBuilder.populate_paths_from_merkletree(merkletree_root, merkle_paths, root_path)
            merkle_paths.sort()

        hash = _ModuleBuilder._hash_from_file_paths(merkle_paths, root_path)
        return hash

    @staticmethod
    def calculate_hash(module_def, content_path=None):
        module_hash = module_def.calculate_hash()

        exclude_function = None
        if content_path:
            ignore_file = get_project_ignore_file(content_path)
            exclude_function = ignore_file.is_file_excluded

        content_hash = _ModuleBuilder._default_content_hash_calculator(exclude_function, content_path)
        module_hash = module_hash + "_" + content_hash

        return module_hash
