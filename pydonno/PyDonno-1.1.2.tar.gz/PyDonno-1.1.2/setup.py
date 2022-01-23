from distutils.core import setup
from distutils.command.install import install
from subprocess import call
class Install(install):
    def run(self):
        install.run(self)
        for line in open('requirements.txt').readlines():
            if len(line) > 1: call(['pip3', 'install', line.replace('\n', '')])
setup(
    name = 'PyDonno',
    version = '1.1.2',
    description = 'All my packages',
    long_description = open('README.md').read().replace('`', '').replace('sh', '').replace('\n', '\n\n'),
    long_description_content_type="text/markdown",
    url = 'https://github.com/donno2048/PyDonno',
    license = 'MIT',
    author = 'Elisha Hollander',
    author_email = 'just4now666666@gmail.com',
    cmdclass = {'install': Install}
)
