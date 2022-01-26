#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Script to run Pyxel as a module.

Examples
--------
$ python -m pyxel --version
Pyxel, version ...

$ python -m pyxel --help
...

$ python -m pyxel --config my_config.yaml
...
"""

from pyxel.run import main

if __name__ == "__main__":
    main(prog_name="python -m pyxel")
