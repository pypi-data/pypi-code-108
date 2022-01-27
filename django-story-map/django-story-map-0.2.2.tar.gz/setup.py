import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name='django-story-map',
    version='0.2.2',
    description="""A django app to create/edit/publish story maps using https://storymap.knightlab.com/""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Peter Andorfer',
    author_email='peter.andorfer@oeaw.ac.at',
    url='https://github.com/acdh-oeaw/django-story-map',
    packages=[
        'story_map',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=3.2,<4',
    ],
    license="MIT",
    zip_safe=False,
    keywords='django-story-map'
)
