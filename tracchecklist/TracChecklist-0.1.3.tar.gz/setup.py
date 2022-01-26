from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name             = 'TracChecklist',
    version          = '0.1.3',
    author           = 'Ralph Ewig',
    author_email     = 'ralph.ewig@sydereal.com',
    description      = "Include checklists in ticket, sourced from wiki pages",

    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://trac-hacks.org/wiki/TracChecklistMacro",
    project_urls={
        "Bug Tracker": "https://trac-hacks.org/report/9?COMPONENT=TracChecklistMacro",
    },

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Framework :: Trac',
    ],

    packages= find_packages(exclude=("test", "*.egg-info",)),
    package_data={ 'checklist': ['htdocs/*', 'plugin.wk']},

    entry_points = {
        'trac.plugins': [
                'checklist.plugin = checklist.plugin',
                'checklist.macros = checklist.macros',
                ],
    }
)
