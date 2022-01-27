from pathlib import Path
import re
from setuptools import setup, find_packages

here = Path(__file__).parent

def read(*parts):
    """ 读取一个文件并返回内容
    """
    return here.joinpath(*parts).read_text(encoding='utf8')

def find_version(*file_paths):
    """ 从 __init__.py 的 __version__ 变量中提取版本号
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def find_requires(*file_paths):
    """ 将提供的 requirements.txt 按行转换成 list
    """
    require_file = read(*file_paths)
    return require_file.splitlines()


classifiers = [
    'Programming Language :: Python :: 3.9',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Operating System :: POSIX :: Linux',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Utilities',
    'License :: OSI Approved :: BSD License',
]

# 使用 flask 的扩展
entry_points = {
    'flask.commands': [
        'pyape=pyape.cli.command:main',
    ]
}

package_data = {
    'pyape.tpl' : ['*.jinja2', '*.py', 'fabconfig/*.py']
}


setup(
    name = "pyape",
    version=find_version('pyape', '__init__.py'),
    description = "The Python Application Programming Environment.",
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author = "zrong",
    author_email = "zrongzrong@gmail.com",
    url = "https://github.com/zrong/pyape",
    license = "BSD 3",
    keywords = "development zrong flask wechat",
    python_requires='>=3.9, <4',
    packages = find_packages(exclude=['test*', 'doc*', 'fabric']),
    install_requires=find_requires('requirements.txt'),
    entry_points=entry_points,
    include_package_data = True,
    zip_safe=False,
    classifiers = classifiers, 
    package_data=package_data
)
