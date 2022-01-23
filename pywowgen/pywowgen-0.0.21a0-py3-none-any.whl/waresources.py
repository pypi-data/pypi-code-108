"""
This is the "resources" module.
"""

import os
from pathlib import Path
import shutil


class waindex:
    """maps a file/folderstructure to resource categories and provides some comfort functions

    uses some white and blacklisting

    index = dict of lists pythons Path Objects

    Tests:

    >>> import os
    >>> tr = waindex('default')
    >>> tr.scan(str(os.path.join(os.environ.get('WOWGEN_EXTRA'), 'res')))
    True

    """

    def __init__(self, name=''):
        self.name = name
        self.index = {}
        self.sourcepath = None
        self.relpaths = {}
        self.filenames = {}
        self.description = None
        self.type_folder_map = {
            'audio': 'audio',
            'templates': 'templates',
            'tilesets': 'tilesets',
            'js': 'js',
            'html': 'html',
            'maps': 'maps',
            'py': 'py',
            'fonts': 'fonts',
            'doc': 'doc',
            'examples': 'examples',
            'sh': 'sh',
            'div': 'div',
            'css': 'css',
            'generated': 'generated'
        }
        self.blacklist = ['.git', '__', '.gitignore']

    def scan(self, sourcepath):
        """returns true if scan happpend without errors"""
        self.sourcepath = os.path.abspath(sourcepath)

        try:
            for mi in self.type_folder_map:
                sf = os.path.abspath(os.path.join(sourcepath, self.type_folder_map[mi]))
                temp_index = list(Path(sf).glob('**/*'))
                # print(temp_index)
                self.relpaths[mi] = []
                self.filenames[mi] = []
                self.index[mi] = []
                for resource in temp_index:
                    blacklisted = False
                    for bl in self.blacklist:
                        if bl in resource.parts:
                            blacklisted = True
                    if not blacklisted:
                        self.relpaths[mi].append(str(resource.relative_to(self.sourcepath)))
                        self.filenames[mi].append(str(resource.name))
                        self.index[mi].append(resource)
            return True
        except Exception as err:
            print(err)
            return False

    def find_resource_path_string(self, resource, restype=None):
        """returns a filepath as string if the given resource and type are within this resources repo OR False"""
        # print('find: ', resource, restype, self.relpaths)
        found = False
        if not restype:
            for mytype in self.relpaths:
                for rtv in self.relpaths[mytype]:
                    # converting to Path() for comparison, because of file paths like / or \
                    if Path(resource) == Path(rtv):
                        found = os.path.abspath(os.path.join(self.sourcepath, resource))
        else:
            try:
                for rtv in self.relpaths[restype]:
                    # converting to Path() for comparison, because of file paths like / or \
                    if Path(resource) == Path(rtv):
                        found = os.path.abspath(os.path.join(self.sourcepath, resource))
            except KeyError:
                raise ValueError('resourcetype {restype} not found')
        return found

    def copy(self, sourcepath, targetpath):

        nsp = os.path.join(self.sourcepath, Path(sourcepath))

        os.makedirs(os.path.split(targetpath)[0], exist_ok=True)
        try:
            shutil.copy(nsp, targetpath)
            return True
        except FileNotFoundError as err:
            return False

    def find_custom_maps_path(self):
        """(path, path)
            json, png
            only if both are found (map and thumbnail)
        """
        ml = []
        for aml in self.index['maps']:
            if str(aml).endswith('.json'):
                ml.append(aml)
        tl = []
        for aml in self.index['maps']:
            if str(os.path.dirname(aml)).endswith('thumbnails'):
                if str(aml).endswith('.png'):
                    tl.append(aml)

        # map ml, tl
        rs = []
        for m in ml:
            mn = str(os.path.basename(m).replace('.json', ''))
            for t in tl:
                tn = str(os.path.basename(t).replace('.png', ''))
                if tn.endswith(mn):
                    rs.append((m, t))

        return rs

    def find_templates_maps_path(self):
        ml = []
        for aml in self.index['templates']:
            if str(os.path.dirname(aml)).endswith('maps'):
                if str(aml).endswith('.json'):
                    ml.append(aml)
        tl = []
        for aml in self.index['templates']:
            if str(os.path.dirname(aml)).endswith('thumbnails'):
                if str(aml).endswith('.png'):
                    tl.append(aml)
        # map ml, tl
        rs = []
        for m in ml:
            mn = str(os.path.basename(m).replace('.json', ''))
            for t in tl:
                tn = str(os.path.basename(t).replace('.png', ''))
                if tn.endswith(mn):
                    rs.append((m, t))

        return rs

    def find_metadata_files_path(self):

        metadata = []
        for mytype in self.relpaths:
            for rtv in self.relpaths[mytype]:

                if rtv.endswith('COPYRIGHT') or rtv.endswith('AUTHORS') or rtv.endswith('LICENSE'):
                    metadata.append(rtv)

        return metadata

    def read(self, sourcepath):
        nsp = os.path.join(self.sourcepath, Path(sourcepath))
        with open(os.path.abspath(nsp), "r") as read_file:
            cnt = read_file.readlines()
        return cnt


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
