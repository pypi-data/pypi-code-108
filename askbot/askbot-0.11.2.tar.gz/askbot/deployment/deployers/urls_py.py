"""Deployes the urls.py file"""
import os
from askbot.deployment.deployers.file_deployer import FileDeployer

class UrlsPy(FileDeployer): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/urls_py.jinja2'

    def get_file_path(self):
        """Returns the target path of the urls.py file"""
        return os.path.join(self.params['proj_dir'], 'urls.py')
