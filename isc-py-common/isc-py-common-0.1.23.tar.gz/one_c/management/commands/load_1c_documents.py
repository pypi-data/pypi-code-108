import configparser
import logging
import os
from datetime import datetime
from os.path import getmtime
from tkinter import *
from tkinter import filedialog
from uuid import UUID
from xml.dom.minidom import parseString

from django.core.management import BaseCommand
from django.db import transaction
from lxml import etree
from tqdm import tqdm

from isc_common import setAttr, str_to_bool
from one_c.models.document_1c import Document_1c
from one_c.models.documents_param_1c import Documents_param_1c
from one_c.models.documents_param_cross_1c import Documents_param_cross_1c
from one_c.models.entity_1c import Entity_1c
from one_c.models.files_1c import Files_1c
from one_c.models.param_type import Param_type

logger = logging.getLogger(__name__)


class V8Exch:
    def __init__(self, pbar, filename):
        self.filename = filename
        self.pbar = pbar
        self.started = False
        self.entities = dict()
        self.attributes = dict()
        self.step = 0
        self.tags = 0

    def start(self, tag, attrib):
        if not self.started:
            m = re.search('({.*})', tag)
            if m:
                ns = m.group(1)
                tag = tag.replace(ns, '')
                if tag == 'Data':
                    self.started = True
        else:
            index = tag.find('CatalogObject.')
            if index == -1:
                self.tag = tag
                self.param_type = self.attributes.get(tag)
                if self.param_type is None:
                    self.param_type, created = Param_type.objects.get_or_create(code=tag)
                    setAttr(self.attributes, tag, self.param_type)
            else:
                tag = tag.replace('CatalogObject.', '')
                self.tag = tag
                self.entity = self.entities.get(tag)
                if self.entity is None:
                    self.entity, created = Entity_1c.objects.get_or_create(code=tag)
                    setAttr(self.entities, tag, self.entity)

                self.step += 1
                # logger.debug(f'step: {self.step}, tags: {self.tags}')

            # logger.debug(f'tag: {tag}')

    def end(self, tag):
        self.tags += 1

    def data(self, data):
        if data.strip() != '':
            # logger.debug(f'tag: {self.tag}, data: {data}')
            if self.tag == 'Ref':
                self.document, created = Document_1c.objects.get_or_create(entity=self.entity, ref=UUID(data.strip()))
                if not created:
                    for documents_param_cross_1c in Documents_param_cross_1c.objects.filter(document=self.document):
                        try:
                            Documents_param_1c.objects.filter(id=documents_param_cross_1c.param).delete()
                            documents_param_cross_1c.delete()
                            documents_param_cross_1c.save()
                        except Exception as ex:
                            logger.error(ex)

                param, created = Documents_param_1c.objects.get_or_create(type=self.param_type, value_uuid=UUID(data.strip()))
                Documents_param_cross_1c.objects.create(document=self.document, param=param)

                if self.pbar:
                    self.pbar.update(1)
            else:
                try:
                    param, created = Documents_param_1c.objects.get_or_create(type=self.param_type, value_uuid=UUID(data.strip()))

                except ValueError:
                    try:
                        param, created = Documents_param_1c.objects.get_or_create(type=self.param_type, value_boolean=str_to_bool(data.strip()))
                    except ValueError:
                        try:
                            param, created = Documents_param_1c.objects.get_or_create(type=self.param_type, value_int=int(data.strip()))
                        except ValueError:
                            try:
                                param, created = Documents_param_1c.objects.get_or_create(type=self.param_type, value_float=float(data.strip()))
                                if created:
                                    logger.debug(f'Created: {param}')
                            except ValueError:
                                param, created = Documents_param_1c.objects.get_or_create(type=self.param_type, value=data.strip())

                Documents_param_cross_1c.objects.create(document=self.document, param=param)

                # logger.debug(f'rec document_param: {document_param}')

    def close(self):
        if self.pbar:
            self.pbar.close()


class Command(BaseCommand):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {}

    config.sections()
    config.read('config.ini')

    help = "Загрузка документов из 1С"
    root = Tk()

    def handle(self, *args, **options):

        try:
            try:
                initialdir = self.config['DEFAULT']['1cdir']
                if not os.path.exists(initialdir):
                    initialdir = None
            except KeyError:
                initialdir = None

            self.root.filename = filedialog.askopenfilename(title="Выбирите файл документов", initialdir=initialdir)
            dir, _ = os.path.split(self.root.filename)
            self.config['DEFAULT']['1cdir'] = dir
            logger.debug(f'filename : {self.root.filename}')
            self.root.withdraw()

            date_modification = datetime.fromtimestamp(getmtime(self.root.filename))
            with transaction.atomic():
                file, created = Files_1c.objects.get_or_create(real_name=self.root.filename, file_modification_time=date_modification, props=Files_1c.props.imp)

                if created:
                    file = open(self.root.filename, 'r')
                    data = file.read()
                    file.close()
                    dom = parseString(data)
                    qty = len(dom.getElementsByTagName('Ref'))

                    pbar = tqdm(total=qty)

                    # with transaction.atomic():
                    parser = etree.XMLParser(target=V8Exch(pbar, self.root.filename))
                    etree.parse(self.root.filename, parser)
                else:
                    logger.warning(f'Файл: {self.root.filename}, уже импортирован !')

                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
        except Exception as ex:
            self.root.withdraw()
            raise ex
