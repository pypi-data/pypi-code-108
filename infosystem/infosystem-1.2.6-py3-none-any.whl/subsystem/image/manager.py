import os
import shutil
from pathlib import Path

from infosystem.common.subsystem import operation
from infosystem.subsystem.file import manager
from infosystem.subsystem.image import tasks
from infosystem.subsystem.image.resource import QualityImage
from infosystem.subsystem.image.handler import ImageHandler
from infosystem.common import exception


class Create(manager.Create):

    def do(self, session, **kwargs):
        super().do(session)

        # TODO (araujobd)  check a better way to improve this
        # only way to validate resolution of image was after
        # save temporary file so if exceeds should trigger rollback
        folder = self.manager.get_upload_folder(self.entity,
                                                self.entity.domain_id)
        error_message = ImageHandler.verify_size_resolution_image(
            folder, self.entity.filename)
        if error_message is not None:
            shutil.rmtree(folder)
            raise exception.BadRequest(error_message)

        return self.entity

    def post(self):
        tasks.process_image(self.upload_folder, self.entity.filename)


class Get(operation.Get):

    def pre(self, session, id, **kwargs):
        self.quality = kwargs.pop('quality', QualityImage.min)

        return super().pre(id=id, session=session)

    def do(self, session, **kwargs):
        file = super().do(session=session, **kwargs)

        folder = self.manager.get_upload_folder(file, file.domain_id)
        filename = file.filename_with_quality(self.quality)

        existingFile = Path(f'{folder}/{filename}')
        if existingFile.is_file() is False and self.quality is not None:
            filename = file.filename_with_quality(None)
            existingFile = Path(f'{folder}/{filename}')

        if existingFile.is_file() is False:
            raise exception.InfoSystemException('File not found!')
        else:
            return folder, filename


class Delete(operation.Delete):

    def post(self):
        # TODO(fdoliveira) Put this in worker
        folder = self.manager.get_upload_folder(self.entity,
                                                self.entity.domain_id)
        shutil.rmtree(folder)


class Manager(manager.Manager):
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

    def __init__(self, driver):
        super().__init__(driver)
        self.create = Create(self)
        self.get = Get(self)
        self.delete = Delete(self)

    def get_upload_folder(self, entity, domain_id):
        base_folder = self._get_base_folder()
        entity_name = type(entity).__name__
        folder = os.path.join(base_folder,
                              entity_name,
                              entity.type_image,
                              self.OPTIONAL_FOLDER,
                              domain_id,
                              entity.id)
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder
