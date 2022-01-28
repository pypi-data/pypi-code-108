from pathlib import Path
import csv
import os

from click import UsageError
from boxsdk.object.folder import Folder


class BoxSync:
    """
    Syncs the parent folder files to Box.

    Compares current files, checks for any missing in Box or any changed locally,
    creates directory structure and finally uploads all files
    """

    def __init__(self, options, api, logger):
        self.api = api
        self.logger = logger
        self.parent_folder_id = options['box_folder_id']
        self.source_folder = Path(options['source_folder_paths'])
        self.glob = '*'
        if ':' in str(self.source_folder):
            self.source_folder, self.glob = str(self.source_folder).split(':')
            self.source_folder = Path(self.source_folder)
        if not self.source_folder.is_dir():
            raise UsageError(f'Source folder {self.source_folder} is not a directory')
        self.changes = []
        self._parent = None

    @property
    def parent_folder(self):
        """
        Gets the parent folder in Box via API GET
        """
        if self._parent:
            return self._parent
        self._parent = self.api.client.folder(self.parent_folder_id).get()
        return self._parent

    def to_path(self, item):
        """
        Converts a Box File/Folder to a filepath from the parent folder
        """
        path_collection = item.get(fields=['path_collection']).path_collection
        item_path = None
        for entry in path_collection['entries']:
            if entry == self.parent_folder:
                item_path = self.source_folder
            elif item_path is not None:
                item_path = item_path / entry.name
        return item_path / item['name']

    def get_box_paths(self, folder_id=None):
        """
        Yields all paths recursively from the parent folder ID
        """
        if folder_id is None:
            folder_id = self.parent_folder_id
        for item in self.api.client.folder(folder_id).get_items():
            yield self.to_path(item), item
            if isinstance(item, Folder):
                yield from self.get_box_paths(item._object_id)

    def __call__(self):
        local_paths = list(self.source_folder.rglob(self.glob))
        local_files = [path for path in local_paths if path.is_file()]
        local_dirs = [path for path in local_paths if path.is_dir()]
        new_dirs = {}

        self.logger.info(f'Syncing {len(local_files)} files in {len(local_dirs) + 1} folders from {self.source_folder}')

        def get_parent(path):
            parent = path.parent
            if parent == self.source_folder:
                return self.parent_folder
            elif parent in box_paths:
                return box_paths[parent]
            elif parent in new_dirs:
                return new_dirs[parent]
            else:
                raise ValueError(f'Unable to resolve folder path: {parent}')

        box_paths = dict(self.get_box_paths())

        # Layout folder/subfolder structure
        for path in local_dirs:
            if path not in box_paths:
                parent = get_parent(path)
                new_dirs[path] = subfolder = self.api.create_folder(parent._object_id, path.name)
                self.changes.append((parent, subfolder))

        # Sync files
        for path in local_files:
            if path not in box_paths:
                parent = get_parent(path)
                new_file = self.api.upload(parent._object_id, path.resolve())
                self.changes.append((parent, new_file))
            else:
                boxfile = box_paths[path]
                size = boxfile.get(fields=['size']).size
                if size != os.stat(path).st_size:
                    updated_file = self.api.update(boxfile._object_id, path.resolve())
                    self.changes.append((get_parent(path), updated_file))

        if not self.changes:
            self.logger.warning('No changes detected')

    def output(self, filename):
        """
        Writes output CSV of what files are synced and their destinations in Box
        """
        with open(filename, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(('Item Type', 'Parent Folder ID', 'Parent Folder Name', 'Item ID', 'Item Name'))
            for parent, item in self.changes:
                writer.writerow([item.__class__.__name__, parent._object_id, parent.name, item._object_id, item.name])
