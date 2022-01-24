import os
from os import path
import logging
from logging.handlers import RotatingFileHandler
import zipfile
import shutil
import fnmatch
from PIL import Image
from configparser import ConfigParser
from . import morph_log
from . import yaml_validator

def un_zipFiles():
    """
        # un_zipFiles
        The function checks the ./contentpacks/ for any .zip files.  If found it unzips into that directory and then moves the zip files to archive. 
    """
    logger = morph_log.get_logger('zpfil')
    archive = os.path.join(os.getcwd(), 'contentpacks', 'archive')
    if not os.path.exists(archive):
        logger.info('Path: '+archive+' not found.')
        os.mkdir(archive)
        logger.info('Created: '+archive)
    path = os.path.join(os.getcwd(), 'contentpacks')
    logger.debug('Content Path: '+path)
    files=os.listdir(path)
    for file in files:
        if file.endswith('.zip'):
            filePath=path+'/'+file
            logger.info('Unzipping: '+filePath)
            zip_file = zipfile.ZipFile(filePath)
            for names in zip_file.namelist():
                zip_file.extract(names,path)
            zip_file.close()
            shutil.move(filePath, archive)
            logger.info('File moved to ./contentpacks/archive: '+filePath)
        else:
            logger.info('Skipping not a zip file: '+file)

def verify_yaml_structure_helper(morpheusComponent, yaml_file):
    logger = morph_log.get_logger('verifyGroup')
    if morpheusComponent in ['groups', 'group']:
        verify_yaml_structure('/groups.py', yaml_file, logger)
    if morpheusComponent in ['roles', 'role']:
        verify_yaml_structure('/roles.py', yaml_file, logger)


def verify_yaml_structure(arg0, yaml_file, logger):
    schema_dir = path.join(path.dirname(__file__), 'schema')
    schemafile = schema_dir + arg0
    configfile = yaml_file
    try:
        yaml_validator.validate(configfile, schemafile)
    except Exception as e:
        logger.error('Exception: ', e)
    


def imageResizer(file):
    if fnmatch.fnmatch(file, '*header_logo*'):
        fixed_height = 76
    if fnmatch.fnmatch(file, '*footer_logo*'):
        fixed_height = 54
    if fnmatch.fnmatch(file, '*login_logo*'):
        fixed_height = 240
    image = Image.open(file)
    height_percent = (fixed_height / float(image.size[1]))
    width_size = int((float(image.size[0]) * float(height_percent)))
    image = image.resize((width_size, fixed_height), Image.NEAREST)
    resizedImage = file
    image.save(resizedImage)
    return resizedImage