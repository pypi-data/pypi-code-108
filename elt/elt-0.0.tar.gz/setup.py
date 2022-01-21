import setuptools

setuptools.setup(
    name="elt",
    version="0.0",
    packages=['elt'],
    entry_points={
        'console_scripts': ['elt=elt:main', ]
    },
)
