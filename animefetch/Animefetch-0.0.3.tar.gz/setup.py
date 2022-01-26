import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION ='0.0.3'
PACKAGE_NAME =  'Animefetch'
AUTHOR = "Tadeo Asael 'Thadeuks'"
AUTHOR_EMAIL = 'ass.hurtado2008@gmail.com'
URL = 'https://github.com/Thadeuks'

LICENSE= 'MIT'
DESCRIPTION= 'Anime Command-Line System Information Tool'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = 'text/markdown'

INSTALL_REQUIRES = [
'colorama',
'psutil'
]

setup(
	name=PACKAGE_NAME,
	version=VERSION,
	description = DESCRIPTION,
	long_description = LONG_DESCRIPTION,
	long_description_content_type = LONG_DESC_TYPE,
	author = AUTHOR,
	author_email = AUTHOR_EMAIL,
	url=URL,
	install_requires = INSTALL_REQUIRES,
	license = LICENSE,
	packages = find_packages(),
	include_package_data = True

	)


