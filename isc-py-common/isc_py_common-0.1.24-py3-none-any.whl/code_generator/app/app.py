from django.db import models

from code_generator.app import model
from code_generator.app.app_mailwindow import AppMainWindow


def os(args):
    pass


class App(model.Model):


    databases_templ = 'ts/datasources/datasource.pmd'
    views_templ = 'python/views.pmd'
    urls_templ = 'python/urls.pmd'

    databases = []
    editors = []
    views = []
    urls = []
    templates = []
    others = []

    def write_entity(self):
        for key, value in self.get_model_attributes():
            if isinstance(value, AppMainWindow):
                setattr(value, 'name_app', self.name_app)
                setattr(value, 'code_app', self.code_app)
                setattr(value, 'path_app', self.path_app)
                value.write_entity()

        for key, value in self.get_model_attributes():
            if isinstance(value, models.Model):
                pass
