# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_midicsv', 'py_midicsv.midi']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['csvmidipy = py_midicsv.cli:csvmidi',
                     'midicsvpy = py_midicsv.cli:midicsv']}

setup_kwargs = {
    'name': 'py-midicsv',
    'version': '3.0.0',
    'description': 'A library for converting MIDI files from and to CSV format',
    'long_description': '# py_midicsv\n\n[![CircleCI](https://circleci.com/gh/timwedde/py_midicsv.svg?style=svg)](https://circleci.com/gh/timwedde/py_midicsv)\n[![Downloads](https://pepy.tech/badge/py-midicsv)](https://pepy.tech/project/py-midicsv)\n\nA Python library inspired by the [midicsv](http://www.fourmilab.ch/webtools/midicsv/) tool created by John Walker. Its main purpose is to bidirectionally convert between the binary `MIDI` format and a human-readable interpretation of the contained data in text format, expressed as `CSV`.\nIf you found this library, you probably already know why you need it.\n\n\n## Installation\n\n`py_midicsv` can be installed via pip:\n```bash\n$ pip install py_midicsv\n```\n\nAlternatively you can build the package by cloning this repository and installing via [poetry](https://github.com/sdispater/poetry):\n```bash\n$ git clone https://github.com/timwedde/py_midicsv.git\n$ cd py_midicsv/\n$ poetry install\n```\n\n\n## Usage\n\n### As a Command Line Tool\n```bash\nUsage: midicsvpy [OPTIONS] INPUT_FILE OUTPUT_FILE\n\n  Convert MIDI files to CSV files.\n\n  midicsv reads a standard MIDI file and decodes it into a CSV file which\n  preserves all the information in the MIDI file. The ASCII CSV file may be\n  loaded into a spreadsheet or database application, or processed by a program\n  to transform the MIDI data (for example, to key transpose a composition or\n  extract a track from a multi-track sequence). A CSV file in the format\n  created by midicsv may be converted back into a standard MIDI file with the\n  csvmidi program.\n\n  Specify an input file and an output file to process it. Either argument can\n  be stdin/stdout.\n\n  Some arguments are kept for backwards-compatibility with the original\n  midicsv tooling. These are marked as NOOP in this command line interface.\n\nOptions:\n  -n, --nostrict  Do not fail on parse/validation errors.\n  -u, --usage     Print usage information (NOOP)\n  -v, --verbose   Print debug information (NOOP)\n  --help          Show this message and exit.\n```\n\n```bash\nUsage: csvmidipy [OPTIONS] INPUT_FILE OUTPUT_FILE\n\n  Convert CSV files to MIDI files.\n\n  csvmidi reads a CSV file in the format written by midicsv and creates the\n  equivalent standard MIDI file.\n\n  Specify an input file and an output file to process it. Either argument can\n  be stdin/stdout.\n\n  Some arguments are kept for backwards-compatibility with the original\n  csvmidi tooling. These are marked as NOOP in this command line interface.\n\nOptions:\n  -n, --nostrict     Do not fail on parse/validation errors.\n  -u, --usage        Print usage information (NOOP)\n  -v, --verbose      Print debug information (NOOP)\n  -z, --strict-csv   Raise exceptions on CSV errors (NOOP)\n  -x, --no-compress  Do not compress status bytes (NOOP)\n  --help             Show this message and exit.\n```\n\n### As a Library\n```python\nimport py_midicsv as pm\n\n# Load the MIDI file and parse it into CSV format\ncsv_string = pm.midi_to_csv("example.mid")\n\nwith open("example_converted.csv", "w") as f:\n    f.writelines(csv_string)\n\n# Parse the CSV output of the previous command back into a MIDI file\nmidi_object = pm.csv_to_midi(csv_string)\n\n# Save the parsed MIDI file to disk\nwith open("example_converted.mid", "wb") as output_file:\n    midi_writer = pm.FileWriter(output_file)\n    midi_writer.write(midi_object)\n```\n\n## Documentation\nA full explanation of the `midicsv` file format can be found [here](https://github.com/timwedde/py_midicsv/blob/master/doc/file-format.md).\n\n## Differences\n\nThis library adheres as much as possible to how the original library works, however generated files are not guaranteed to be entirely identical when compared bit-by-bit.\nThis is mostly due to the handling of meta-event data, especially lyric events, since the encoding scheme has changed. The original library did not encode some of the characters in the Latin-1 set, while this version does.\n',
    'author': 'Tim Wedde',
    'author_email': 'timwedde@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/timwedde/py_midicsv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
