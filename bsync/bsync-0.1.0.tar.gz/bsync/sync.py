from pathlib import Path
import csv
import os

from boxsdk.object.folder import Folder


class BoxSync:

    def __init__(self, options, api, logger):
        self.api = api
        self.logger = logger
        self.parent_folder_id = options['box_folder_id']
        self.parent_folder = api.client.folder(self.parent_folder_id).get()
        self.source_folder = Path(options['source_folder'])
        self.changes = []

    def to_path(self, item):
        path_collection = item.get(fields=['path_collection']).path_collection
        item_path = None
        for entry in path_collection['entries']:
            if entry == self.parent_folder:
                item_path = self.source_folder
            elif item_path is not None:
                item_path = item_path / entry.name
        return item_path / item['name']

    def get_box_paths(self, folder_id=None):
        if folder_id is None:
            folder_id = self.parent_folder_id
        for item in self.api.client.folder(folder_id).get_items():
            yield self.to_path(item), item
            if isinstance(item, Folder):
                yield from self.get_box_paths(item._object_id)

    def __call__(self):
        box_paths = dict(self.get_box_paths())
        local_paths = list(self.source_folder.rglob('*'))
        local_files = [path for path in local_paths if path.is_file()]
        local_dirs = [path for path in local_paths if path.is_dir()]
        new_dirs = {}

        self.logger.info(f'Syncing {len(local_files)} files in {len(local_dirs)} folders from {self.source_folder}')

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
        with open(filename, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(('Item Type', 'Parent Folder ID', 'Parent Folder Name', 'Item ID', 'Item Name'))
            for parent, item in self.changes:
                writer.writerow([item.__class__.__name__, parent._object_id, parent.name, item._object_id, item.name])
