# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from datetime import datetime

if __name__ == "__main__":
    year = datetime.now().year
    for root, directories, files in os.walk("."):
        for filename in files:
            if filename.endswith(".py"):
                path = os.path.join(root, filename)
                if datetime.fromtimestamp(os.path.getmtime(path)).year == year:
                    with open(path, "r") as file:
                        lines = file.readlines()

                    if (
                        lines
                        and "Copyright " in lines[0]
                        and "Portmod Authors" in lines[0]
                    ):
                        lines[0] = f"# Copyright 2019-{year} Portmod Authors"
                        with open(path, "w") as file:
                            for line in lines:
                                print(line.rstrip(), file=file)
