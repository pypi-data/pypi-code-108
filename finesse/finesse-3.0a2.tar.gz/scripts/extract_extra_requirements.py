"""Extract extra dependencies from `setup.cfg`.

Call with the path to `setup.cfg` and the extras section name(s) to extract as
arguments.

This is used by the CI to install test and documentation dependencies without the need
for separate `requirements-test.txt` and `requirements-doc.txt` files.
"""

import sys
import configparser


if __name__ == "__main__":
    conf = configparser.ConfigParser()
    conf.read(sys.argv[1])

    requirements = set(
        [conf["options.extras_require"][extra].strip() for extra in sys.argv[2:]]
    )

    for requirement in requirements:
        print(requirement)
