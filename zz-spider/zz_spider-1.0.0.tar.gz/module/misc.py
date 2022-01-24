import sys
import subprocess


class Utils(object):

    def install(self, package):
        subprocess.call([sys.executable, "-m", "pip", "install", package])