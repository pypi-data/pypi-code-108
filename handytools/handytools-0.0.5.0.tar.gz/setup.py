from distutils.core import setup

# read the contents of your README file
# https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='handytools',         # How you named your package folder (MyLib)
    packages=['handytools'],   # Chose the same as "name"
    # Start with a small number and increase it with every change you make
    version='0.0.5.0',
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='So far, contains string and file processing tools.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Yuhang Tao',                   # Type in your name
    author_email='yuhang.tao.email@gmail.com',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/TITC/handytools',
    # I explain this later on
    download_url='https://github.com/TITC/handytools/archive/refs/tags/0.0.5.0.tar.gz',
    # Keywords that define your package best
    keywords=['nlp', 'file', 'regex'],
    install_requires=[            # I get to this in a second
        "fitz",
        "jsonlines",
        "line_profiler",
        "numpy",
        "pandas",
        "opencv_python",
        "pandas",
        "pdfplumber",
        "Pillow",
        "tqdm"
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.8',
    ],
)
