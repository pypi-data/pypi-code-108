import re
import sys
from pathlib import Path


def main(argv):
    part = argv[0].lower() if len(argv) > 0 else "minor"
    Jenkinsfile = Path("./Jenkinsfile")
    pyprojectfile = Path("./pyproject.toml")
    with Jenkinsfile.open("r", encoding="utf-8") as fin:
        data = fin.read()
        for line in data.split(fin.newlines):
            if "MAJOR_VERSION" in line:
                result = re.search(r'MAJOR_VERSION\s*=\s*"([0-9]+)"', line)
                if result:
                    major = int(result.group(1))
                    if part == "major":
                        to_replace = result.group(0)
                        by_replace = f"MAJOR_VERSION = \"{major + 1}\""
            if "MINOR_VERSION" in line:
                result = re.search(r'MINOR_VERSION\s*=\s*"([0-9]+)"', line)
                if result:
                    minor = int(result.group(1))
                    if part == "minor":
                        to_replace = result.group(0)
                        by_replace = f"MINOR_VERSION = \"{minor + 1}\""
    data = data.replace(to_replace, by_replace)
    with Jenkinsfile.open("wt") as fout:
        fout.write(data)

    depend_string = f"{major}.{minor}.0,<{major}.{minor + 1}.0"
    new_depend_string = f"{major}.{minor + 1}.0,<{major}.{minor + 2}.0"
    with pyprojectfile.open("r", encoding="utf-8") as fin:
        data = fin.read()
    data = data.replace(depend_string, new_depend_string)
    with pyprojectfile.open("wt") as fout:
        fout.write(data)


if __name__ == "__main__":
    main(sys.argv[1:])
