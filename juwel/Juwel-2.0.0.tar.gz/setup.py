from setuptools import setup, find_packages

setup(
   name='Juwel',
   license='GPL',
   version='2.0.0',
   description='Sidecar file generator',
   author='Gefan Qian',
   author_email='qian@cbs.mpg.de',
   packages=find_packages(),
   install_requires=['tk', 'tkcalendar'],
   python_requires='>=3.6',

   include_package_data=True,
   package_data={'Juwel': []},

   entry_points={
        'console_scripts': [
            'juwel=Juwel.Main:main',
        ],
    },
)
