from pathlib import Path
import subprocess
import sys

def main():

    binary_name = Path(sys.argv[0]).name
    prefix = Path(__file__).parent.parent
    bin_dirs = {'bin'}

    binary_path = ""

    for dir in bin_dirs:
        path = prefix / Path(dir) / binary_name
        if path.is_file():
            binary_path = str(path)
            break

        path = Path(str(path) + ".exe")
        if path.is_file():
            binary_path = str(path)
            break

    if not Path(binary_path).is_file():
        name = binary_path if binary_path != "" else binary_name
        raise RuntimeError(f"Failed to find binary: { name }")

    sys.argv[0] = binary_path

    result = subprocess.run(args=sys.argv, capture_output=False)
    exit(result.returncode)

if __name__ == "__main__" and len(sys.argv) > 1:
    sys.argv = sys.argv[1:]
    main()