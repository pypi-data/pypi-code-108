"""
Validate that the data can be loaded successfully and move the data to the production folder
"""
from enum import IntEnum
import typing as ty
import json
import strax
from warnings import warn
import os
import shutil
import glob
from collections import defaultdict
from reprox import core


class ValidationLevel(IntEnum):
    SHALLOW = 0
    DEEP = 1


class RunValidation:
    """
    Check that a directory (corresponding to a single datatype is
    """

    def __init__(self,
                 path: str,
                 context: strax.Context = None,
                 mode: ty.Union[int, ValidationLevel] = ValidationLevel.SHALLOW,
                 ):
        self.path = path
        self.mode = mode
        self.st = context
        if mode > ValidationLevel.SHALLOW and context is None:
            raise ValueError('Context is a required argument if a DEEP '
                             'validation of the data is performed')

    def find_error(self) -> str:
        """Run several checks on a path to see if the processing was done correctly"""
        if self._is_temp():
            return 'is_temp_folder'

        md = self._open_metadata()
        if not md:
            return 'has_no_metadata'

        if self._did_fail(md):
            return 'has_exception'

        if self._misses_chunks(md):
            return 'misses_chunks'

        key = os.path.split(self.path)[-1]
        split_key = key.split('-')

        if self._wrong_format(split_key):
            return 'is_wrong_format'

        if self.mode == ValidationLevel.DEEP:
            run, data_type, lineage_hash = split_key
            if self._different_hash(run, data_type, lineage_hash):
                return 'cannot_validate_different_hash'

            if self._cannot_load(run, data_type):
                return 'loading_error'

        return False

    def _is_temp(self):
        if '_temp' in self.path:
            warn(f'{self.path} is not finished', UserWarning)
            return True

    def _did_fail(self, md):
        if 'exception' in md:
            warn(f'{self.path} has an exception', UserWarning)
            return True

    def _misses_chunks(self, md):
        n_files = os.listdir(self.path)
        n_chunks = len(n_files) - 1  # metadata
        chunks = [c.get('n') > 0 for c in md['chunks']]
        if n_chunks != sum(chunks):
            warn(f'{self.path} misses chunks?!', UserWarning)
            return True

    def _different_hash(self, run, data_type, lineage_hash):
        context_lineage_hash = self.st.key_for(run, data_type).lineage_hash
        if lineage_hash != context_lineage_hash:
            warn(f'Lineage hash differs from context. Expected '
                 f'{lineage_hash}, got {context_lineage_hash} for '
                 f'{data_type}', UserWarning)
            return True

    def _cannot_load(self, run, data_type):
        st = self.st.new_context()
        st.storage = [
            strax.DataDirectory(
                os.path.split(self.path)[0],
                readline=False)]
        try:
            for _ in st.get_iter(run, data_type, progress_bar=False):
                pass
        except Exception as e:
            warn(f'{self.path} cannot be loaded due to {e}', UserWarning)
            return True

    @staticmethod
    def _wrong_format(split_key):
        if len(split_key) != 3:
            warn(f'{split_key} is not correct format?!', UserWarning)
            return True
        return False

    def _open_metadata(self) -> dict:
        files = glob.glob(os.path.join(self.path, '*'))
        for f in files:
            if 'metadata' in f:
                md_path = f
                break
        else:
            return {}

        with open(md_path, mode='r') as f:
            return json.loads(f.read())


def change_ownership(path, group):
    shutil.chown(path, group=group)
    # read write execute
    os.chmod(path, 0o777)


def move_folder(path: str,
                destination_folder: str = core.config['context']['destination_folder'],
                group='xenon1t-admins',
                validation_level: int = ValidationLevel.SHALLOW,
                context: ty.Optional[strax.Context] = None,
                ) -> ty.Union[str, None]:
    """
    Move data from path into the destination folder and change the ownership of the folder

    :param path: The folder to move
    :param destination_folder: The folder where the <path> folder should be moved to
    :param group: Name of the group that the permissions should be set to
    :param validation_level: the level at which to validate the data:
        - ValidationLevel.SHALLOW: <0> for basic validation
        - ValidationLevel.DEEP: <1> where we actually try loading the
            data with (requires a context)
    :param context: for when the validation_level is set to ValidationLevel.DEEP
    :return: error string if an error occurred
    :raises FileExistsError: when there is already a folder at the destination path
    """
    validation = RunValidation(path, context=context, mode=validation_level)
    error_string = validation.find_error()
    if error_string:
        return error_string
    change_ownership(path, group)
    dest_path = os.path.join(destination_folder, os.path.split(path)[-1])
    if os.path.exists(dest_path):
        raise FileExistsError(f'{dest_path} already exists!')
    shutil.move(path, dest_path)
    return None


def move_all(
        source_folder: str = os.path.join(core.config['context']['base_folder'], 'strax_data'),
        destination_folder: str = core.config['context']['destination_folder'],
        **move_kwargs):
    """
    Move data from all folders in <source_folder> into the destination
    folder and change the ownership of the folder


    :param source_folder: The main folder where to look for folders to move
    :param destination_folder: The folder where the <path> folder should be moved to

    :param move_kwargs: Takes the following kwargs:
        :group: Name of the group that the permissions should be set to
        :validation_level: the level at which to validate the data:
            - ValidationLevel.SHALLOW: <0> for basic validation
            - ValidationLevel.DEEP: <1> where we actually try loading the
                data with (requires a context)
        :context: for when the validation_level is set to ValidationLevel.DEEP

    :return: None
    """
    folders = sorted(glob.glob(os.path.join(source_folder, '*')))
    fails = defaultdict(list)
    for folder in strax.utils.tqdm(
            folders,
            desc='move folders',
            disable=not core.config['display']['progress_bar'],
    ):
        try:
            error_string = move_folder(folder,
                                       destination_folder=destination_folder,
                                       **move_kwargs)
            if error_string:
                fails[error_string].append(folder)
        except FileExistsError:
            fails['FileExistsError'].append(folder)
        except Exception as e:
            print(f'Ran into {e}')  # most likely a permission error
            fails['Other'].append(folder)
    for key, value in fails.items():
        core.log.warning(f'{key}, {len(value)}')
        if len(value) < 5:
            for v in value:
                core.log.info(f'\t{v}')
    core.log.info(
        f'Did {len(folders)}. Ran into {sum(len(v) for v in fails.values())} failures'
    )
