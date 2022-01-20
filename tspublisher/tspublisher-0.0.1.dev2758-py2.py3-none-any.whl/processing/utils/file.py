import os

import publisher.settings as settings
from publisher.utils import get_procedure_code


class ProcedureFileManager(object):

    def __init__(self, procedure):
        self._procedure_code = procedure.code
        self._ensure_structure_exists()

        self.phase_files = [PhaseFileManager(p, self._procedure_code) for p in procedure.phases]

    def _ensure_structure_exists(self):
        for d in [self.base_directory, self.asset_directory, self.build_asset_directory, self.more_info_directory,
                  self.overview_directory, self.devices_directory, self.eula_directory, self.csv_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    @property
    def base_directory(self):
        return os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, self._procedure_code)

    @property
    def procedure_file(self):
        return os.path.join(self.base_directory, 'procedure.yml')

    @property
    def asset_directory(self):
        return os.path.join(self.base_directory, 'assets')

    @property
    def build_asset_directory(self):
        return os.path.join(self.base_directory, 'build_assets')

    @property
    def more_info_directory(self):
        return os.path.join(self.build_asset_directory, 'moreInfo')

    @property
    def overview_directory(self):
        return os.path.join(self.build_asset_directory, 'overview')

    @property
    def devices_directory(self):
        return os.path.join(self.build_asset_directory, 'devices')

    @property
    def eula_directory(self):
        return os.path.join(self.build_asset_directory, 'eula')

    @property
    def csv_directory(self):
        return os.path.join(self.build_asset_directory, 'csv')


class PhaseFileManager(object):

    def __init__(self, phase, procedure_code):
        self._procedure_code = procedure_code
        self.phase_code = phase.code

        self._ensure_structure_exists()

    def _ensure_structure_exists(self):
        for d in [self.base_directory, self.asset_directory, self.translation_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    @property
    def base_directory(self):
        return os.path.join(self.procedure_directory, self.phase_code)

    @property
    def procedure_directory(self):
        return os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, self._procedure_code)

    @property
    def phase_file(self):
        return os.path.join(self.base_directory, 'phase.yml')

    @property
    def asset_directory(self):
        return os.path.join(self.base_directory, 'assets')

    @property
    def translation_directory(self):
        return os.path.join(self.base_directory, 'translations')


class DeliveryFileManager(object):

    def __init__(self, procedure_code, phases, vbs):
        self._procedure_code = procedure_code
        self.phases = phases
        self.vbs = vbs
        self.phase_directories = {}

        if self.vbs:
            self.base_directory = settings.VBS_ROOT
        else:
            self.base_directory = settings.CG_APP5_ROOT

        self._ensure_procedure_structure_exists()
        self._ensure_phase_structure_exists()

    def _ensure_procedure_structure_exists(self):
        for d in [self.procedure_directory, self.proc_thumbnail_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    def _ensure_phase_structure_exists(self):
        for phase in self.phases:
            self.phase_code = phase.code
            for d in [self.phase_directory, self.phase_thumbnail_directory, self.graphics_directory, self.pip_directory,
                      self.project_directory, self.widget_directory]:
                if not os.path.exists(d):
                    os.makedirs(d)
                self.phase_directories[self.phase_code] = {
                    "base_directory": self.phase_directory,
                    "thumbnail_directory": self.phase_thumbnail_directory,
                    "graphics_directory": self.graphics_directory,
                    "pip_directory": self.pip_directory,
                    "project_directory": self.project_directory,
                    "widget_directory": self.widget_directory,
                }

    @property
    def phase_directory(self):
        return os.path.join(self.base_directory, self.phase_code)

    @property
    def procedure_directory(self):
        return os.path.join(self.base_directory, self._procedure_code)

    @property
    def proc_thumbnail_directory(self):
        return os.path.join(self.procedure_directory, 'thumbnails')

    @property
    def phase_thumbnail_directory(self):
        return os.path.join(self.phase_directory, 'thumbnails')

    @property
    def graphics_directory(self):
        return os.path.join(self.phase_directory, 'graphics')

    @property
    def pip_directory(self):
        return os.path.join(self.phase_directory, 'pipSource')

    @property
    def project_directory(self):
        return os.path.join(self.phase_directory, 'projectFiles')

    @property
    def widget_directory(self):
        return os.path.join(self.phase_directory, 'widgetGraphics')


def get_procedure_yaml_file():
    return os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, get_procedure_code(), 'procedure.yml')


def get_all_procedure_yaml_files():

    ignore_directories = ['build_assets', 'assets', 'translations']

    yaml_files = []
    for subdir, dirs, files in os.walk(settings.PROCEDURE_CHECKOUT_DIRECTORY):

        directories = os.path.normpath(subdir).split(os.sep)
        if any(d in directories for d in ignore_directories) or len([d for d in directories if d.startswith('.')]) > 0:
            continue

        yaml_files += [os.path.join(subdir, f) for f in files if f.endswith('.yml')]

    return yaml_files
