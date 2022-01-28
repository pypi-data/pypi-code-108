import configparser
import logging
import os
import shutil
import zipfile
from os.path import isdir, isfile, getsize
from tkinter.filedialog import askdirectory

from django.conf import settings
from django.core.management import BaseCommand
from files_blk.models.files import Files
from files_blk.models.files_group import Files_group
from isc_common import replace_alt_set, delete_drive_leter
from isc_common.logger.Logger import Logger
from isc_common.oss.functions import mekeDirs, copyTwo

from ivc.kompas.interaction.interaction_kompas import IsNotDirectory

logger = logging.getLogger(__name__)
logger.__class__ = Logger


class Command(BaseCommand):
    help = "Test"

    config = configparser.ConfigParser()
    config['DEFAULT'] = {}

    config.sections()
    config.read('config.ini')

    def handle(self, *args, **options):
        self.cnt = 0
        self.not_recorded = []

        def rec_file(file):

            dist = f'{settings.EXP_FILES_STORE}{os.sep}{replace_alt_set(delete_drive_leter(file))}'
            file_size = getsize(file)

            try:
                Files.objects.using('files_blk').get(
                    group=self.file_group,
                    path=delete_drive_leter(file),
                    file_size=file_size
                )

                logger.info(f'file exist : {dist}')
            except Files.DoesNotExist:
                dir, _file = os.path.split(dist)
                if mekeDirs(dir, logger, exist_ok=True):
                    if copyTwo(file, dist):
                        self.cnt += 1
                        logger.info(f'file recorded ({self.cnt}) : {dist}')
                    else:
                        self.not_recorded.append(file)
                        logger.warning(f'file not recorded ({self.cnt}) : {dist}')

        def walk_dir(dir):
            if isdir(dir):
                # logger.debug(f'dir: {dir}')
                for path_section in os.listdir(dir):
                    # logger.debug(path_section)
                    full_path = replace_alt_set(f"{dir}{os.sep}{path_section}")
                    if isdir(full_path):
                        walk_dir(dir=full_path)
                    elif isfile(full_path) and full_path.lower().endswith('.spw'):
                        rec_file(file=full_path)
                    elif isfile(full_path) and full_path.lower().endswith('.cdw'):
                        rec_file(file=full_path)
                    elif isfile(full_path) and full_path.lower().endswith('.pdf'):
                        rec_file(file=full_path)
                    elif isfile(full_path) and full_path.lower().endswith('.xml'):
                        rec_file(file=full_path)
            else:
                raise IsNotDirectory(f"{dir} is not directory.")

        def zipdir(path, ziph):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file))

        try:
            try:
                initialdir = self.config['DEFAULT']['file_blk']
                if not os.path.exists(initialdir):
                    initialdir = None
            except KeyError:
                initialdir = None

            self.directory = askdirectory(title='Выбирите каталог размещения файлов', initialdir=initialdir)
            logger.info(f'Выбран каталог : {self.directory}')

            self.full_start_path = f"{settings.EXP_FILES_STORE}{os.sep}{replace_alt_set(delete_drive_leter(self.directory))}"
            if os.path.exists(self.full_start_path):
                shutil.rmtree(self.full_start_path)

            self.file_group, created = Files_group.objects.using('files_blk').get_or_create(code=f'{os.altsep}{delete_drive_leter(self.directory)}')

            walk_dir(dir=replace_alt_set(self.directory))

            zipfname = f'{self.full_start_path}.zip'
            logger.info(f'Start Ziping. ({zipfname})')
            zipf = zipfile.ZipFile(zipfname, 'w')
            zipdir(self.full_start_path, zipf)
            zipf.close()
            logger.info(f'Start Ziped. ({zipfname})')

            self.config['DEFAULT']['file_blk'] = self.directory

            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

            logger.info(f'Done. ({self.cnt})\n')
            logger.info(f'Not recorded\n')
            for nr in self.not_recorded:
                logger.info(nr)

        except Exception as ex:
            raise ex
