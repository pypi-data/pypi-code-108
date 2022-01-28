import logging
import os

from code_generator.app.app import App
from code_generator.app.app_mailwindow import AppMainWindow
from code_generator.app.model import Model

logger = logging.getLogger(__name__)


class WinAppModel(Model):
    name = None
    mainWindow = None
    appImageDir = None
    isc_templ = 'Isc.pmd'
    startfunction_templ = 'start_function.pmd'

    def write_entity(self):
        for key, value in self.get_model_attributes():
            if isinstance(value, App):
                setattr(value, 'name_app', self.name)
                setattr(value, 'code_app', f'{self.name}.{key}')
                setattr(value, 'path_app', f'{self.name}{os.sep}{key}')
                value.write_entity()

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)

        if self.name is None:
            raise Exception(f'Не задано имя модели.')

        logger.debug(f'Инициализация приложения: {self.dbl_qutes_str(self.name)}')


