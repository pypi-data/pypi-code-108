from setuptools import setup, find_packages
import re

with open('README.md') as f:
    long_description = f.read()

version = ''
with open('colorgb/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set')

def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements


setup(
    name='colorgb',
    version=version,
    author='LyQuid',
    author_email='lyquidpersonal@gmail.com',
    description='A Python packages to recoloring default terminal text',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT License',
    url='https://github.com/LyQuid12/colorgb',
    project_urls={
        "Source Code": "https://github.com/LyQuid12/colorgb",
        "Discord": "https://discord.gg/qpT2AeYZRN",
        "Issue tracker": "https://github.com/LyQuid12/colorgb/issues"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    keywords=["python", "color", "colorgb", "coloring", "recoloring",  "rgb"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Android'
    ]
)
