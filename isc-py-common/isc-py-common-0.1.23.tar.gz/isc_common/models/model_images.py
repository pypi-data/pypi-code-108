import logging
import os
from os.path import expanduser

from django.conf import settings
from django.db import transaction
from isc_common import Stack
from isc_common.fields.files import make_REPLACE_FILE_PATH, make_REPLACE_IMAGE_PATH
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.number import flen

logger = logging.getLogger(__name__)


class Model_imagesQuerySet(AuditQuerySet):
    pass


class Model_imagesManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Model_imagesQuerySet(self.model, using=self._db)


class ImageNotFound(Exception):
    pass


class Model_images(AuditModel):
    @classmethod
    def get_image(cls, file_name, path=None):
        if file_name is None:
            return None

        if os.altsep is not None:
            have_path = file_name.find(os.altsep) != -1
        else:
            have_path = file_name.find(os.sep) != -1

        if have_path:
            if os.altsep is None:
                file_name1 = f'{settings.OLD_SITE_BASE_DIR}{file_name}'.replace(os.sep, '\\')
            else:
                file_name1 = f'{settings.OLD_SITE_BASE_DIR}{file_name}'.replace(os.altsep, os.sep)
            try:
                return cls.objects.get(path__upper=file_name1.upper()).path
            except cls.DoesNotExist:
                return None

        query = cls.objects.filter(file_name=file_name).order_by('-date')
        if query.count() == 0:
            return None
        else:
            _list = list(map(lambda x: x.path, query))
            if path is None:
                return _list[0]

            for item in _list:
                if item.find(path) != -1:
                    return item
            return None

    @classmethod
    def rec_update(cls, main_model, image, code, keyimage, result=None, self_image_field=False, defaults=None):
        if self_image_field is False:
            from isc_common.models.image_types import Image_types
            image_type, _ = Image_types.objects.get_or_create(code=code, keyimage=keyimage)

            if isinstance(main_model, int):
                res, _ = cls.objects.update_or_create(image=image, type=image_type, main_model_id=main_model, defaults=defaults)
            else:
                res, _ = cls.objects.update_or_create(image=image, type=image_type, main_model=main_model, defaults=defaults)

            if result is not None:
                result.push(res, lambda item, stack: flen(filter(lambda x: x.id == res.id, stack)) > 0)
        else:
            raise Exception('Not implementation')
            # eval( f'main_model._meta.concrete_model.objects.filter({pk_name}=main_model.{pk_name}).update({image_field_name}=image)' , dict() , dict( image=image , main_model=main_model ) )

    @classmethod
    def update_or_create_image(cls, main_model, path, file_name, keyimage, self_image_field=False, code=None, exception=True, defaults=None, o_ssh_client=None):
        from isc_common.models.images import Images
        # from lfl_admin.common.models.site_lfl_images import Site_lfl_images

        result = Stack()

        if file_name is None or file_name.strip() == '':
            return result

        if (code is None or code.strip() == '') or (path is None or path.strip() == ''):
            code = path

        with transaction.atomic():
            # full_name_images = Site_lfl_images.get_image(file_name=file_name, path=path)
            full_name_images = []

            if len(full_name_images) == 0 and file_name is not None:
                if exception is True:
                    raise ImageNotFound(f'{file_name} : not found')
                else:
                    logger.error(f'{file_name} : not found !!!')

            for full_name_image in full_name_images:
                if full_name_image is not None:

                    zero = False

                    full_name_image_replaced = make_REPLACE_IMAGE_PATH(full_name_image)
                    home = expanduser("~")
                    localpath = f"{home}/tmp"
                    if not os.path.exists(localpath):
                        os.makedirs(localpath)

                    if o_ssh_client is None:
                        o_ssh_client = settings.SSH_CLIENTS.client(settings.OLD_FILES)

                    if o_ssh_client.exists(full_name_image_replaced):
                        size = o_ssh_client.getsize(full_name_image_replaced)
                        if size == 0:
                            image.real_name = full_name_image_replaced
                            image.size = 0
                            image.attfile = ''
                            image.save()
                            continue

                        _, _file_name = os.path.split(full_name_image_replaced)
                        # logger.debug( f'file_name: {_file_name}, size: {size}' )
                        image = Images.objects.getOptional(file_name=_file_name, size=size)
                        if image is None:
                            image = Images.objects.getOptional(real_name=full_name_image_replaced, size=size)

                            if (image is not None):
                                image.file_name = _file_name
                                image.size = size
                                image.save()
                            else:
                                image = Images.objects.create(real_name=full_name_image_replaced, file_name=_file_name, size=size)

                    else:
                        zero = True
                        logger.debug(f'{full_name_image_replaced} : not found')

                    if not zero:
                        cls.rec_update(
                            code=code,
                            defaults=defaults,
                            image=image,
                            keyimage=keyimage,
                            main_model=main_model,
                            result=result,
                            self_image_field=self_image_field,
                        )
                        # logger.debug( f'{file_name} : found' )

            return result

    @classmethod
    def replace_image(cls, image, _image, django_model_images, imports, main_model, keyimage):
        for _import in imports:
            eval(f'exec("{_import}")')

        s4compile = f'''{django_model_images}.objects.filter(image_id={image.id}).update(image_id={_image.id})'''
        code = compile(s4compile, '<string>', 'eval')
        eval(code)
        cls.rec_update(
            code=code,
            image=_image,
            main_model=main_model,
            keyimage=keyimage,
        )

    @classmethod
    def update_or_create_image1(cls, main_model, code, path, keyimage, image_id, django_model_images, imports, defaults=None):
        from isc_common.models.images import Images

        imports = imports.split(',')

        if image_id is None:
            return None

        with transaction.atomic():
            image = Images.objects.get(id=image_id)
            full_name_image = image.real_name
            if full_name_image is not None:

                full_name_image_replaced = make_REPLACE_IMAGE_PATH(full_name_image)

                localpath = f"{expanduser('~')}/tmp"
                if not os.path.exists(localpath):
                    os.makedirs(localpath)

                o_ssh_clients = settings.SSH_CLIENTS.client(settings.OLD_FILES)
                if o_ssh_clients.exists(full_name_image_replaced):
                    size = o_ssh_clients.getsize(full_name_image_replaced)
                    _, fileName = os.path.split(full_name_image_replaced)

                    _image = Images.objects.getOptional(real_name=full_name_image_replaced, size=size)
                    if _image is None:
                        _image = Images.objects.getOptional(real_name=fileName, size=size)
                    else:
                        _image.real_name = fileName;
                        _image.save()

                    if _image is not None:
                        attfile = make_REPLACE_FILE_PATH(str(_image.attfile))

                        if isinstance(settings.FILES_STORE, dict):
                            exists = settings.SSH_CLIENTS.client(settings.FILES_STORE).exists(attfile)
                        else:
                            exists = os.path.exists(attfile)

                        if str(attfile) != '' and exists is True:
                            cls.replace_image(
                                image=image,
                                _image=_image,
                                django_model_images=django_model_images,
                                imports=imports,
                                main_model=main_model,
                                keyimage=keyimage,
                            )
                            return _image.id
                        else:
                            _image.size = 0
                            _image.save()

                    image1, created = Images.create_update(
                        id=image.id,
                        real_file_name=full_name_image_replaced,
                        tmp_dir_name=localpath,
                    )

                    if image1.id != image.id:
                        cls.replace_image(
                            image=image,
                            _image=image1,
                            django_model_images=django_model_images,
                            imports=imports,
                            main_model=main_model,
                            keyimage=keyimage,
                        )
                        return image1.id
                else:
                    return None

                cls.rec_update(
                    code=code,
                    keyimage=keyimage,
                    image=image,
                    main_model=main_model,
                    defaults=defaults,
                )
                return image.id
            return image.id

    objects = Model_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Базовый класс'
        abstract = True
