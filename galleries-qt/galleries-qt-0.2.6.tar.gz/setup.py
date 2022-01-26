import setuptools
import subprocess
import sys


def get_last_version():
    bash_command = "git describe --tags --abbrev=0 --match v[0-9]*"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    outputstr = str(output)
    outputstr = outputstr[3:-3]  # "b'vXX.XX.XX\\n'" becomes "XX.XX.XX"
    outputstr = outputstr.replace('-', '.')
    major, minor, patch, *_ = outputstr.split('.')
    version = f'{major}.{minor}.{patch}'
    return version


def bump_patch(version: str):
    major, minor, patch = version.split('.')
    bumped = str(int(patch) + 1)
    return f'{major}.{minor}.{bumped}'


def push_new_version_as_tag(version):
    bash_command = f"git tag v{version}"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    bash_command = f"git push origin v{version}"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


if __name__ == '__main__':
    last_version = get_last_version()
    version = bump_patch(last_version)

    if sys.argv[1] == 'pushtag':
        push_new_version_as_tag(version)
    else:
        with open("README.md", "r") as fh:
            long_description = fh.read()

        setuptools.setup(
            name="galleries-qt",
            version=version,
            author="Miguel Nicolás-Díaz",
            author_email="miguelcok27@gmail.com",
            description="Qt implementation to manage galleries.",
            long_description=long_description,
            long_description_content_type="text/markdown",
            url="https://github.com/mnicolas94/galleries_qt",
            packages=[
                'galleries_qt',
                'galleries_qt.parser_widgets'
            ],
            install_requires=[
                'galleries>=0.2.4',
                'mnd_utils',
                'mnd_qtutils',
                'numpy',
                'opencv-python',
                'propsettings_qt>=0.2.1',
                'pyrulo-qt>=0.3.1',
                'PySide2',
            ],
            classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                'Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
            ],
            python_requires='>=3.6',
            include_package_data=True,
            package_data={'':  ['*.ui']},
        )
