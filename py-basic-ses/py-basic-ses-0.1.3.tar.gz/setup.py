from setuptools import setup

with open("README.md", "r") as fh:
    readme_long_description = fh.read()

setup(
    name='py-basic-ses',
    version='0.1.3',    
    description="py-basic-ses provides a command line application and library to send emails via Amazon Web Services' Simple Email Service, or AWS SES, API by leveraging the boto3 library.",
    long_description=readme_long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shinyshoes404/py-basic-ses',
    author='shinyshoes',
    author_email='shinyshoes404@protonmail.com',
    license='MIT License',
    packages=['py_basic_ses'],
    package_dir={'':'src'},
    entry_points = { 'console_scripts' : ['send-test=py_basic_ses.entry:send_test_email',
                    'send-email=py_basic_ses.entry:send_email']},
    install_requires=[
        'boto3>=1.17',
        'click'    
    ],

    extras_require={
        # To install requirements for dev work use 'pip install -e .[dev]'
        'dev': ['coverage', 'mock']
    },

    python_requires = '>=3.8.*,!=3.11.*',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',           
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)
