# -*- coding: utf-8 -*-
"""
Radiance folder structure module.

This module includes classes for writing and reading to / from a Radiance folder
structure.

See https://github.com/ladybug-tools/radiance-folder-structure#radiance-folder-structure

"""
import os
import re
import shutil

import honeybee_radiance_folder.config as config

from .folderutil import (parse_aperture_groups, parse_dynamic_scene, parse_states, 
    combined_receiver, _nukedir)
from .gridutil import parse_grid_info, parse_grid_json

try:
    from ConfigParser import SafeConfigParser as CP
except ImportError:
    # python 3
    from configparser import ConfigParser as CP


class _Folder(object):
    """Radiance folder base class structure.

    Attributes:
        folder (str): Path to project folder.

    Args:
        folder (str): Path to project folder as a string. The folder will be created
            on write if it doesn't exist already.

    """

    __slots__ = ('_folder',)

    def __init__(self, folder):
        self._folder = self._as_posix(os.path.normpath(folder))

    @staticmethod
    def _load_config_file(cfg_file):
        """Load a folder config file and return it as JSON."""

        cfg_file = cfg_file or os.path.join(os.path.dirname(__file__), 'folder.cfg')
        assert os.path.isfile(cfg_file), 'Failed to find config file at: %s' % cfg_file
        parser = CP()
        parser.read(cfg_file)
        config = {}
        for section in parser.sections():
            config[section] = {}
            for option in parser.options(section):
                config[section][option] = \
                    parser.get(section, option).split('#')[0].strip()
        return config, cfg_file.replace('\\', '/')

    @property
    def folder(self):
        """Return full path to project folder."""
        return self._folder

    def _find_files(self, subfolder, pattern, rel_path=True):
        """Find files in a subfolder.

        Args:
            subfolder (str): A subfolder.
            pattern (str): A regex pattern to match the target file.
            rel_path (bool): Return relative path to root folder.
        """
        folder = os.path.join(self.folder, subfolder)
        filtered_files = [
            self._as_posix(os.path.normpath(os.path.join(folder, f)))
            for f in os.listdir(folder)
            if re.search(pattern, f)
        ]

        if rel_path:
            # FIX relative path
            return [
                self._as_posix(os.path.relpath(fi, self.folder))
                for fi in filtered_files
            ]
        else:
            return filtered_files

    @staticmethod
    def _get_file_name(path):
        """Get file name with no extention."""
        base = os.path.basename(path)
        return os.path.splitext(base)[0]

    @staticmethod
    def _as_posix(path):
        """Replace \\ with / in path.

        Once we remove support for Python 2 we should use pathlib module instead.
        """
        return path.replace('\\', '/')

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.folder)


class ModelFolder(_Folder):
    """Radiance Model folder.

    Radiance Model folder includes all geometry and geometry metadata including
    modifiers. See Radiance folder structure repository for more information:

    https://www.github.com/ladybug-tools/radiance-folder-structure

    Args:
        project_folder (str): Project folder as string. The folder will be created on
            write if it doesn't exist already.
        model_folder (str): Model folder name (default: model).
        config_file (str): Optional config file to modify the default folder names. By
            default ``folder.cfg`` in ``honeybee-radiance-folder`` will be used.

    .. code-block:: shell

        └─model                  :: radiance model folder
            ├───aperture         :: static apertures description
            ├───aperture_group   :: apertures groups (AKA window groups) - optional
            │   └───interior     :: interior aperture groups - optional
            ├───bsdf             :: in-model BSDF files and transmittance matrix files
            ├───grid             :: sensor grids
            ├───ies              :: electric lights description
            ├───scene            :: static scene description
            ├───scene_dynamic    :: dynamic scene description - optional
            │   └───indoor       :: indoor dynamic scene description - optional
            └───view             :: indoor and outdoor views

    """
    # required keys in config file
    CFG_KEYS_REQUIRED = {
        'GLOBAL': ['static_apertures'],
        'APERTURE': ['path', 'geo_pattern', 'mod_pattern', 'blk_pattern'],
        'SCENE': ['path', 'geo_pattern', 'mod_pattern', 'blk_pattern']
    }
    CFG_KEYS_CHOICE = {
        'GRID': ['path', 'grid_pattern', 'info_pattern'],
        'VIEW': ['path', 'view_pattern', 'info_pattern']
    }
    CFG_KEYS_OPTIONAL = {
        'APERTURE-GROUP': ['path', 'states'],
        'INTERIOR-APERTURE-GROUP': ['path', 'states'],
        'BSDF': ['path', 'bsdf_pattern'],
        'IES': ['path', 'ies_pattern'],
        'DYNAMIC-SCENE': ['path', 'states'],
        'INDOOR-DYNAMIC-SCENE': ['path', 'states']
    }
    CFG_KEYS = {
        k: v
        for d in [CFG_KEYS_REQUIRED, CFG_KEYS_CHOICE, CFG_KEYS_OPTIONAL]
        for k, v in d.items()
    }

    __slots__ = (
        '_config', '_config_file', '_aperture_group_interior', '_aperture_group',
        '_aperture_groups_load', '_dynamic_scene', '_dynamic_scene_indoor',
        '_dynamic_scene_load'
    )

    def __init__(self, project_folder, model_folder='model', config_file=None):
        _Folder.__init__(self, os.path.abspath(project_folder))
        self._config, self._config_file = self._load_config_file(config_file)
        self._config['GLOBAL']['root'] = model_folder
        self._validate_config()
        self._aperture_group = None
        self._aperture_group_interior = None
        self._dynamic_scene = None
        self._dynamic_scene_indoor = None
        self._aperture_groups_load = True  # boolean to keep track of first load
        self._dynamic_scene_load = True  # boolean to keep track of first load

    @classmethod
    def from_model_folder(cls, model_folder, config_file=None):
        """Use model folder instead of project folder.

        Args:
            model_folder (str): Model folder as string. The folder will be created on
            write if it doesn't exist already.
        config_file (str): Optional config file to modify the default folder names. By
            default ``folder.cfg`` in ``honeybee-radiance-folder`` will be used.
        """
        project_folder, folder_name = os.path.split(model_folder)
        return cls(project_folder, folder_name, config_file)

    def model_folder(self, full=False):
        """Model root folder.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        if full:
            return self._as_posix(os.path.abspath(
                os.path.join(self.folder, self._config['GLOBAL']['root'])
            ))
        else:
            return self._as_posix(self._config['GLOBAL']['root'])

    def _get_folder_name(self, folder_cfg_name):
        """Get folder name from config using folder key."""
        return self._as_posix(self._config[folder_cfg_name]['path'])

    def _get_folder(self, folder_cfg_name, full=False):
        """Get path to folder from config using folder key."""
        p = os.path.join(self.model_folder(full), self._config[folder_cfg_name]['path'])
        return self._as_posix(os.path.normpath(p))

    def aperture_folder(self, full=False):
        """Aperture folder path.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        return self._get_folder('APERTURE', full)

    def aperture_group_folder(self, full=False, interior=False):
        """Aperture group folder path.

        Args:
            full: A boolean to note if the path should be a full path or a relative path
                (default: False).
            interior: Set to True to get the path for interior aperture group folder.

        Returns:
            Path to folder.
        """
        if not interior:
            return self._get_folder('APERTURE-GROUP', full)
        else:
            return self._get_folder('INTERIOR-APERTURE-GROUP', full)

    def bsdf_folder(self, full=False):
        """BSDF folder path.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        return self._get_folder('BSDF', full)

    def grid_folder(self, full=False):
        """Sensor grids folder path.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        return self._get_folder('GRID', full)

    def ies_folder(self, full=False):
        """IES folder path.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        return self._get_folder('IES', full)

    def scene_folder(self, full=False):
        """Scene folder path.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        return self._get_folder('SCENE', full)

    def dynamic_scene_folder(self, full=False, indoor=False):
        """Dynamic scene folder path.

        Args:
            full: A boolean to note if the path should be a full path or a relative path
                (default: False).
            indoor: Set to True to get the path for indoor dynamic scene folder.

        Returns:
            Path to folder.
        """
        if not indoor:
            return self._get_folder('DYNAMIC-SCENE', full)
        else:
            return self._get_folder('INDOOR-DYNAMIC-SCENE', full)

    def view_folder(self, full=False):
        """View folder path.

        Args:
            full: A boolean to weather the path should be a full path or a relative path
                (default: False).

        Returns:
            Path to folder.
        """
        return self._get_folder('VIEW', full)

    def _validate_config(self):
        """Validate config dictionary."""
        for k, v in self.CFG_KEYS.items():
            assert k in self._config, \
                '{} is missing from config file sections.'.format(k)
            for i in v:
                assert i in self._config[k], \
                    '{} option is missing from {} section.'.format(i, k)

    @property
    def has_aperture_group(self):
        """Returns true if model has at least one aperture group."""
        # check if states file exist
        states_file = os.path.join(
            self.aperture_group_folder(full=True),
            self._config['APERTURE-GROUP']['states']
        )
        states_file_interior = os.path.join(
            self.aperture_group_folder(full=True, interior=True),
            self._config['APERTURE-GROUP']['states']
        )

        # check for the interior aperture group
        if os.path.isfile(states_file) or os.path.isfile(states_file_interior):
            return True
        return False

    @property
    def has_dynamic_scene(self):
        """Return True if model has dynamic scene.

        This check does not include aperture groups. Use ``has_aperture_group`` instead.
        """
        # check if states file exist
        states_file = os.path.join(
            self.dynamic_scene_folder(full=True),
            self._config['DYNAMIC-SCENE']['states']
        )
        states_file_indoor = os.path.join(
            self.dynamic_scene_folder(full=True),
            self._config['INDOOR-DYNAMIC-SCENE']['states']
        )

        if os.path.isfile(states_file) or os.path.isfile(states_file_indoor):
            return True
        # check for the interior aperture group
        return False

    def view_matrix_files(self, aperture):
        """Files to be included in view matrix calculation for an aperture."""
        # find the room and include the room shell geometry.
        # include the blacked out version of the other apertures in the room.
        # include indoor geometries with the room.
        raise NotImplementedError()

    def daylight_matrix_files(self, aperture, receiver=None):
        """Files to be included in daylight matrix calculation for an aperture.

        Target can be Sky or another aperture.
        """
        # find the room and include the room shell geometry.
        # include the rest of the scene except for indoor geometries for that room.
        # here is a place that light-path is necessary to be able to know what is indoor
        # and what is outdoor.
        raise NotImplementedError()

    def aperture_files(self, black_out=False, rel_path=True):
        """Return list of files for apertures.

        This list includes both geometry and modifier files. This method will raise a
        ValueError if it cannot find a modifier file with the same name as the geometry
        file.

        Args:
            black_out (str): Set black_out to True for "isolated" studies for aperture
                groups.
            rel_path (str): Set rel_path to False for getting full path to files. By
                default the path is relative to study folder root.
        """
        cfg = self._config['APERTURE']
        pattern = cfg['geo_pattern']
        geometry_files = self._find_files(
            self.aperture_folder(full=True), pattern, rel_path
        )
        pattern = cfg['blk_pattern'] if black_out else cfg['mod_pattern']
        modifier_files = self._find_files(
            self.aperture_folder(full=True), pattern, rel_path
        )
        return self._match_files(modifier_files, geometry_files)

    def scene_files(self, black_out=False, rel_path=True):
        """Return list of files for scene.

        Args:
            black_out (str): Set black_out to True for direct sunlight studies.
            rel_path (str): Set rel_path to False for getting full path to files. By
                default the path is relative to study folder root.
        """
        cfg = self._config['SCENE']
        pattern = cfg['geo_pattern']
        geometry_files = self._find_files(
            self.scene_folder(full=True), pattern, rel_path
        )
        pattern = cfg['blk_pattern'] if black_out else cfg['mod_pattern']
        modifier_files = self._find_files(
            self.scene_folder(full=True), pattern, rel_path
        )
        return self._match_files(modifier_files, geometry_files)

    def grid_files(self, rel_path=True, group=None):
        """Return list of grid files."""
        cfg = self._config['GRID']
        pattern = cfg['grid_pattern']
        if not group:
            grid_files = self._find_files(
                self.grid_folder(full=True), pattern, rel_path
            )
        else:
            grid_files = self._find_files(
                os.path.join(self.grid_folder(full=True), group), pattern, rel_path
            )
        return grid_files

    def grid_info_files(self, rel_path=True):
        """Return list of grid information files."""
        cfg = self._config['GRID']
        pattern = cfg['info_pattern']
        grid_info_files = self._find_files(
            self.grid_folder(full=True), pattern, rel_path
        )
        return grid_info_files

    def view_files(self, rel_path=True):
        """Return list of view files."""
        cfg = self._config['VIEW']
        pattern = cfg['view_pattern']
        view_files = self._find_files(
            self.view_folder(full=True), pattern, rel_path
        )
        return view_files

    def view_info_files(self, rel_path=True):
        """Return list of view information files."""
        cfg = self._config['VIEW']
        pattern = cfg['info_pattern']
        view_info_files = self._find_files(
            self.view_folder(full=True), pattern, rel_path
        )
        return view_info_files

    def aperture_groups(self, interior=False, reload=False):
        """List of apertures groups.

        Args:
            interior (bool): Boolean switch to return interior dynamic apertures.
            reload (bool): Dynamic geometries are loaded the first time this
                method is called. To reload the files set reload to True.
        Returns:
            A list of dynamic apertures.
        """
        if reload or self._aperture_groups_load:
            # load dynamic apertures
            self._load_aperture_groups()

        self._aperture_groups_load = False
        return self._aperture_group_interior if interior else self._aperture_group

    def aperture_groups_states(self, full=False, interior=False):
        """Return states information for aperture groups.
        Arg:
            full: A boolean to note if the path should be a full path or a relative path
                (default: False).
            interior: Set to True to get the states information for the interior aperture 
                groups.
        """
        apt_group_folder = self.aperture_group_folder(full=full, interior=interior)
        if interior:
            states_file = os.path.join(
                apt_group_folder, self._config['INTERIOR-APERTURE-GROUP']['states'])
        else:
            states_file = os.path.join(
                apt_group_folder, self._config['APERTURE-GROUP']['states'])
        return parse_states(states_file)

    def combined_receivers(self, folder='receivers', auto_mtx_path=True):
        """Write combined receiver files to folder.

        This function writes a combined receiver file of the aperture groups for all
        grids in the folder. It will look for the light paths (aperture groups) of the 
        grid and include only aperture groups that has a mtx file. This is intended for 
        matrix-based daylight simulations, e.g. 3-phase, in which a view matrix is 
        calculated. The combined receiver file allow multiple view matrices to be 
        calculated at once, while still saving the result of each aperture group in a 
        unique view matrix file.

        Arg:
            folder: A path of the target folder to write files to (default: 'receivers').
            auto_mtx_path: If set to True, then the path of the view matrices will be
                specified automatically.
        Returns:
            A dictionary containing grid identifiers as keys and the receiver rad files
            as values.
        """
        grids = self.grid_data_all()
        apt_group_folder = self.aperture_group_folder(full=False)

        states = self.aperture_groups_states(full=True)

        if not os.path.isdir(folder):
            os.mkdir(folder)

        receiver_dict = dict()

        # find the light_path for each grid
        for grid in grids.values():
            light_path = grid['light_path']
            # remove the static windows
            # another way is to check for the ones which has a mtx file.
            aperture_groups = [
                p[0] for p in light_path if p[0] in states and 'vmtx' in states[p[0]][0]
            ]
            # write combined receiver for grid
            receiver_file = combined_receiver(
                grid['identifier'],
                apt_group_folder,
                aperture_groups,
                folder, add_output_header=auto_mtx_path)

            receiver_dict[grid['identifier']] = receiver_file

        return receiver_dict

    def dynamic_scene(self, indoor=False, reload=False):
        """List of dynamic non-aperture geometries.

        Args:
            indoor (bool): A boolean to indicate if indoor dynamic scene files should be
                returned (default: False).
            reload (bool): Dynamic geometries are loaded the first time this
                method is called. To reload the files set reload to True.
        """
        if reload or self._dynamic_scene_load:
            self._load_dynamic_scene()

        return self._dynamic_scene_indoor if indoor \
            else self._dynamic_scene

    def grid_info(self, is_model=False):
        """Parse the appropriate grids_info file to return high level information about
        the sensor grids contained in the model folder.

        Args:
            is_model: If set to True, the _model_grids_info.json, which is
                written out after simulations will be parsed. Else the _info.json will be
                parsed. Defaults to False as the _info.json file is always expected to be
                present.

        Returns:
            The list containing information about sensor grids that are written to the
                folder after model export.
        """
        if is_model:
            info_json = os.path.join(self.grid_folder(full=True),
                                     '_model_grids_info.json')
        else:
            info_json = os.path.join(self.grid_folder(full=True), '_info.json')

        return parse_grid_info(info_json)

    def grid_data_all(self, info_from_model=False):
        """ This is an internal function that for a specified info_json, returns the
        consolidated grid data ,that includes grid names,counts and identifiers, as a
        single dictionary.

        Args:
            info_from_model: If set to True, data will be retrieved using
            _model_grids_info.json, which is written out after simulations.Else the
            _info.json will be used. Defaults to False as the _info.json file is always
            expected to be present.
        Returns:
            A dictionary containing consolidated grid data for the entire folder.
        """

        grid_info = self.grid_info(is_model=info_from_model)
        grid_folder = self.grid_folder(full=True)

        grid_data_dict = {}

        if not grid_info:
            return None
        else:
            for grid in grid_info:
                grid_id = grid.pop('full_id')
                grid_data_dict[grid_id] = parse_grid_json(
                    os.path.join(grid_folder, grid_id + '.json'))
                grid_data_dict[grid_id].update(grid)
            return grid_data_dict

    def write(self, folder_type=0, cfg=None, overwrite=False):
        """Write an empty model folder.

        Args:
            folder_type: An integer between -1-2.
                * -1: no grids or views
                * 0: grid-based
                * 1: view-based
                * 2: includes both views and grids
            cfg (dict): A dictionary with folder name as key and True or False as
                value. You can pre-defined from ``config`` module. Default is a
                grid-based ray-tracing folder.
            overwrite (bool): Set to True to overwrite the folder if it already exist.

        Returns:
            path to folder.
        """
        assert -1 <= folder_type <= 2, 'folder_type must be an integer between -1-2.'

        # always copy the input cfg to ensure it's not mutated by the folder_type
        cfg = dict(config.minimal) if not cfg else dict(cfg)

        if folder_type == 0:
            cfg['GRID'] = True
        elif folder_type == 1:
            cfg['VIEW'] = True
        elif folder_type == 2:
            cfg['GRID'] = True
            cfg['VIEW'] = True

        root_folder = self.model_folder(full=True)
        if overwrite:
            _nukedir(root_folder)

        if not overwrite and os.path.isdir(root_folder):
            raise ValueError(
                'Model folder already exist: %s\nSet overwrite to True'
                ' if you want the folder to be overwritten.' % root_folder
            )
        for category in self.CFG_KEYS:
            if category == 'GLOBAL':
                continue
            if not cfg[category]:
                continue
            directory = os.path.join(root_folder, self._config[category]['path'])
            if not os.path.exists(directory):
                os.makedirs(directory)
            elif not overwrite:
                raise ValueError('{} already exist.'.format(directory))

        shutil.copy2(self._config_file, root_folder)
        return self._as_posix(root_folder)

    @staticmethod
    def _match_files(first, second):
        """Match to list of files.

        Ensure for every file in list one there is a file with the same name in list two.
        Return a new list which merges the first and the second list and puts the files
        with the same name after each other.

        This method is particularly useful for matching modifier files with geometry
        files.
        """
        first_no_ext = [os.path.splitext(f)[0] for f in first]
        second_no_ext = [os.path.splitext(f)[0] for f in second]
        combined = []
        for c, f in enumerate(first_no_ext):
            try:
                index = second_no_ext.index(f)
            except IndexError:
                raise ValueError('Failed to find matching modifier for %s' % first[c])
            combined.append(first[c])
            combined.append(second[index])
        return combined

    def _load_aperture_groups(self):
        """Try to load interior and exterior dynamic apertures from folder."""
        int_folder = self.aperture_group_folder(full=True, interior=True)
        ext_folder = self.aperture_group_folder(full=True)

        states = self._config['INTERIOR-APERTURE-GROUP']['states']
        self._aperture_group_interior = \
            parse_aperture_groups(
                os.path.join(int_folder, states),
                bsdf_folder=self.bsdf_folder(full=True)
            )

        states = self._config['APERTURE-GROUP']['states']
        self._aperture_group = \
            parse_aperture_groups(
                os.path.join(ext_folder, states),
                bsdf_folder=self.bsdf_folder(full=True)
            )

    def _load_dynamic_scene(self):
        """Try to load indoor and outdoor dynamic scene from folder."""
        folder = self.dynamic_scene_folder(full=True)
        states = self._config['DYNAMIC-SCENE']['states']
        self._dynamic_scene = \
            parse_dynamic_scene(os.path.join(folder, states))

        indoor_folder = self.dynamic_scene_folder(full=True, indoor=True)
        states = self._config['INDOOR-DYNAMIC-SCENE']['states']
        self._dynamic_scene_indoor = \
            parse_dynamic_scene(os.path.join(indoor_folder, states))
