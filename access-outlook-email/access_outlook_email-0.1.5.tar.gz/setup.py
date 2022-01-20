from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent


VERSION = '0.1.5'
DESCRIPTION = 'Send/Save Emails & Attachments via Outlook'
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="access_outlook_email",
    version=VERSION,
    author="Valentin Baier",
    author_email="valentin_baier@gmx.de",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['exchangelib'],
    keywords=['python', 'email', 'outlook', 'send', 'send email', 'save', 'save email'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
