import setuptools
import versioneer

# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html#development-mode
setuptools.setup(version=versioneer.get_version(), cmdclass=versioneer.get_cmdclass())
